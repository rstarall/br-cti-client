import asyncio
import tkinter as tk
from collections import deque
import psutil
import threading
from datetime import datetime
from tkinter import ttk
import darkdetect
import sv_ttk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scapy.all import sniff
import numpy as np
from core.Defender import Defender
from core.Tools import capture_traffic
from utils.logger import log
import utils.config as config


class FixedSizeQueue:
    """
    A fixed-size queue implementation using deque.

    :param max_length: The maximum number of elements in the queue.
    :type max_length: int
    """

    def __init__(self, max_length):
        self.queue = deque(maxlen=max_length)

    def push(self, item):
        """
        Add an item to the queue.

        :param item: The item to be added.
        """
        self.queue.append(item)

    def get_data(self):
        """
        Retrieve all elements in the queue as a list.

        :return: List of queue elements.
        :rtype: list
        """
        return list(self.queue)


def monitor_traffic(interface, target_ip, receive_queue, sent_queue, stop_event):
    """
    Monitors network traffic for a specific IP address and updates traffic statistics.

    :param interface: Network interface to monitor.
    :type interface: str
    :param target_ip: The IP address to track.
    :type target_ip: str
    :param receive_queue: Queue storing received bytes.
    :type receive_queue: FixedSizeQueue
    :param sent_queue: Queue storing sent bytes.
    :type sent_queue: FixedSizeQueue
    :param stop_event: Event to signal monitoring should stop.
    :type stop_event: threading.Event
    """
    while not stop_event.is_set():
        recv_bytes = 0
        sent_bytes = 0

        def packet_callback(packet):
            """ Callback function to process captured packets. """
            nonlocal recv_bytes, sent_bytes
            if 'IP' in packet:
                ip_src = packet['IP'].src
                ip_dst = packet['IP'].dst
                packet_size = len(packet)
                if ip_dst == target_ip:
                    recv_bytes += packet_size
                elif ip_src == target_ip:
                    sent_bytes += packet_size

        # Capture packets with the specified filter
        sniff(iface=interface, filter=f"ip host {target_ip}", prn=packet_callback, timeout=config.UPDATE_GAP)
        receive_queue.push(recv_bytes)
        sent_queue.push(sent_bytes)


def plot_traffic(receive_list, sent_list):
    """
    Creates a traffic plot showing received and sent bytes over time.

    :param receive_list: List of received traffic values.
    :type receive_list: list
    :param sent_list: List of sent traffic values.
    :type sent_list: list
    :return: Matplotlib figure object.
    :rtype: matplotlib.figure.Figure
    """
    fig, ax = plt.subplots()
    ax.plot(receive_list, label='Received', color='red')
    ax.plot(sent_list, label='Sent', color='green')
    ax.legend()
    ax.set_xlabel('time')
    ax.set_ylabel('traffic(bytes)')
    ax.set_title('traffic monitor')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    return fig


def calculate_y_params(max_value):
    """
    Calculates appropriate y-axis limits and grid intervals.

    :param max_value: The maximum value in the dataset.
    :type max_value: int
    :return: Tuple containing the top value and gap value.
    :rtype: tuple
    """
    gap_value = config.DEFAULT_GAP_VALUE
    top_value = config.MAX_THRESHOLD
    if max_value > config.MAX_THRESHOLD:
        top_value = int((int(max_value / config.DEFAULT_GAP_VALUE) + 1) * config.DEFAULT_GAP_VALUE)
        gap_value = max(int(top_value / config.GAP_COUNT), config.DEFAULT_GAP_VALUE)
        if top_value % gap_value != 0:
            gap_value = config.DEFAULT_GAP_VALUE
    return top_value, gap_value


def update_plot(fig, receive_list, sent_list):
    """
    Updates the traffic monitoring plot with new data.

    :param fig: The figure object to update.
    :type fig: matplotlib.figure.Figure
    :param receive_list: List of received traffic values.
    :type receive_list: list
    :param sent_list: List of sent traffic values.
    :type sent_list: list
    """
    if len(receive_list) == 0 or len(sent_list) == 0:
        return
    ax = fig.gca()
    ax.clear()
    receive_array = np.array(receive_list)
    sent_array = np.array(sent_list)
    if receive_array.size == 0 and sent_array.size == 0:
        max_value = 1
    else:
        max_value = np.max(np.stack([receive_array, sent_array]))
    ax.plot(receive_list, label='Received', color='red')
    ax.plot(sent_list, label='Sent', color='green')
    ax.legend()
    ax.set_xlabel('time')
    ax.set_ylabel('traffic(bytes)')
    ax.set_title('traffic monitor')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_xticks([])  # 隐藏x轴刻度
    top_value, gap_value = calculate_y_params(max_value)
    ax.set_ylim(-200, top_value)
    ax.set_yticks(range(0, top_value + 1, gap_value))
    fig.tight_layout()
    fig.canvas.draw()


class DefenseWindow:
    """
    A GUI application for DDoS attack detection and defense.

    This class provides functionalities to monitor network traffic, detect DDoS attacks,
    and implement defense mechanisms. The GUI is built using Tkinter.
    """

    def __init__(self, r):
        """
        Initialize the DefenseWindow.

        :param r: The Tkinter root window.
        """
        self.root = r
        sv_ttk.set_theme(darkdetect.theme())
        self.root.title("DDoS攻击检测与防御原型系统：攻击防御界面")
        self.root.geometry("950x700")
        self.root.resizable(False, False)
        self.root.iconbitmap("D:\Other_file\Project\DDoShield\\assets\d.ico")
        self.create_layout()
        self.stop_event = threading.Event()
        self.defense_stop_event = threading.Event()
        # Preload Defender in a background thread to prevent UI freezing
        self.defender = None  # Used to store Defender instances
        self.load_defender_thread = threading.Thread(target=self.load_defender, daemon=True)
        self.load_defender_thread.start()

    def load_defender(self):
        """
        Load the Defender module in the background to prevent UI freezing.
        """
        self.insert_to_terminal("Defense module is loading, please wait (module loading process takes 10 to 30 seconds)...")
        try:
            self.defender = Defender()
            self.insert_to_terminal("The defense module has been loaded and the defense can be started.")
        except Exception as e:
            self.insert_to_terminal(f"Defense module loading failed: {e}")

    def create_layout(self):
        """
        Load the Defender module in the background to prevent UI freezing.
        """
        ttk.Label(self.root, text="攻击防御界面", font=("微软雅黑", 16)).pack(side="top", pady=10)
        self.start_button = ttk.Button(self.root, command=self.start_monitor, text="开始监控", width=10)
        self.start_button.place(x=30, y=120)
        self.stop_button = ttk.Button(self.root, command=self.stop_monitor, text="停止监控", width=10,
                                      state=tk.DISABLED)
        self.stop_button.place(x=30, y=400)
        self.start_defense_button = ttk.Button(self.root, command=self.start_defense, text="启动防御", width=10)
        self.start_defense_button.place(x=800, y=120)
        self.stop_defense_button = ttk.Button(self.root, command=self.stop_defense, text="停止防御", width=10,
                                              state=tk.DISABLED)
        self.stop_defense_button.place(x=800, y=400)
        self.canvas_frame = ttk.Frame(self.root, width=100, height=100)
        self.canvas_frame.place(x=150, y=50)
        self.receive_list = []
        self.sent_list = []
        fig = plot_traffic(self.receive_list, self.sent_list)
        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        ttk.Label(self.root, text="终端输出", font=("微软雅黑", 14)).place(x=430, y=550)
        self.terminal_output = tk.Text(self.root, width=133, height=8)
        self.terminal_output.place(x=9, y=580)

    def get_current_time(self):
        """
        Get the current time formatted as a string.

        :return: The current timestamp in format [YYYY-MM-DD HH:MM:SS].
        """
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    def insert_to_terminal(self, message):
        """
        Insert a message into the terminal output.

        :param message: The message to display.
        """
        timestamp = self.get_current_time()
        self.terminal_output.insert(tk.END, f"{timestamp} {message}\n")
        self.terminal_output.yview(tk.END)

    def start_monitor(self):
        """
        Start network traffic monitoring.
        """
        self.insert_to_terminal("Start monitoring...")
        log("Online analysis starts traffic monitoring.")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        interface = None
        interfaces = psutil.net_if_addrs()
        for name, addresses in interfaces.items():
            if config.NETWORK_INTERFACE in name:
                interface = name
                break
        if interface is None:
            self.insert_to_terminal("No network card named '以太网' found, please check!")
            return
        self.receive_queue = FixedSizeQueue(config.TIME_WINDOW)
        self.sent_queue = FixedSizeQueue(config.TIME_WINDOW)
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(
            target=monitor_traffic,
            args=(interface, config.TARGET_IP, self.receive_queue, self.sent_queue, self.stop_event)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.update_plot_periodically(interface)

    def update_plot_periodically(self, interface):
        """
        Periodically updates the traffic plot with new data.

        :param interface: str
            The network interface being monitored.

        This method retrieves the latest network traffic data from the receive and sent queues,
        updates the plot, and schedules the next update if monitoring is still active.
        """
        receive = self.receive_queue.get_data()
        sent = self.sent_queue.get_data()
        update_plot(self.canvas.figure, receive, sent)
        if not self.stop_event.is_set():
            self.root.after(1, self.update_plot_periodically, interface)

    def stop_monitor(self):
        """
        Stop network traffic monitoring.
        """
        self.insert_to_terminal("Stop monitoring...")
        log("Online analysis stop flow monitoring.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.stop_event.set()
        if self.monitor_thread.is_alive():
            self.monitor_thread.join()

    def start_defense(self):
        """
        Start the DDoS defense mechanism.
        """
        if self.defender is None:
            self.insert_to_terminal("The defense module has not been loaded yet. Please wait until the module is loaded before starting the defense...")
            return
        self.insert_to_terminal("Activate defense...")
        log("Online analysis starts defense.")
        self.start_defense_button.config(state=tk.DISABLED)
        self.stop_defense_button.config(state=tk.NORMAL)
        self.defense_stop_event.clear()
        self.defense_thread = threading.Thread(target=self.run_defense, daemon=True)
        self.defense_thread.start()

    def run_defense(self):
        """
         Executes the defense mechanism against potential DDoS attacks.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while not self.defense_stop_event.is_set():
            self.insert_to_terminal("Capturing traffic...")
            capture_traffic()
            ddos_flag, malicious_radio_parameter = self.defender.defense(config.PCAP_PATH)
            if ddos_flag:
                self.insert_to_terminal("There is a DDoS attack in the current network!")
            else:
                self.insert_to_terminal("There is no DDoS attack in the current network...")

            flag, malicious_ip = self.defender.do_defense(ddos_flag, malicious_radio_parameter)
            if flag:
                self.insert_to_terminal(f"Target malicious source: {malicious_ip}")
                self.insert_to_terminal("Access control has been deployed!")
            # Ensure that the stop event can be detected immediately
            self.defense_stop_event.wait(config.DEFENSE_INTERVAL)
        # Ensure asyncio event loop is closed properly
        loop.call_soon_threadsafe(loop.stop)
        loop.run_forever()
        loop.close()

    def stop_defense(self):
        """
        Stop the DDoS defense mechanism.
        """
        self.insert_to_terminal("Stop defending...")
        log("Online analysis stop defense.")
        self.start_defense_button.config(state=tk.NORMAL)
        self.stop_defense_button.config(state=tk.DISABLED)
        self.defense_stop_event.set()  # Set the signal so that the thread can exit normally
        # Ensure that the thread exists and is active to avoid UI freezing
        if hasattr(self, "defense_thread") and self.defense_thread.is_alive():
            self.defense_thread.join(timeout=1)  # 1 second timeout to prevent blocking the UI


if __name__ == "__main__":
    root = tk.Tk()
    sv_ttk.set_theme(darkdetect.theme())
    app = DefenseWindow(root)
    root.mainloop()
