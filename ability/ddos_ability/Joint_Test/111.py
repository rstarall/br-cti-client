import re

text = "Microsoft Windows 10 1709 - 1909"
match = re.search(r"Windows 10", text)
if match:
    print(match.group())  # 输出: Windows 10


text = "Microsoft Windows 7 SP0 - SP1, Windows Server 2008 SP1, Windows Server 2008 R2, Windows 8, or Windows 8.1 Update 1"
match = re.search(r"Windows 7", text)
if match:
    print(match.group())  # 输出: Windows 10


#

text = "Linux 2.6.32"
match = re.search(r"Linux", text)
if match:
    print(match.group())  # 输出: Windows 10

# os_name_full = '"' + node['os_name'] + '"'

os_name_full = "Microsoft Windows 7 SP0 - SP1, Windows Server 2008 SP1, Windows Server 2008 R2, Windows 8, or Windows 8.1 Update 1"
if "Windows 7" in os_name_full:
    os_name = "Windows 7"

elif "Windows 10" in os_name_full:
    os_name = "Winoows 10"

elif "Linux" in os_name_full:
    os_name = "Linux"

else:
    os_name = os_name_full
print(os_name)
