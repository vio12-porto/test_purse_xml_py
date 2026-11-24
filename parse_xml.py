

import sys
import xml.etree.ElementTree as ET


def get_text(element, path, default="-"):
    """Ambil teks dari sub-elemen; kalau tidak ada, kembalikan default."""
    found = element.find(path)
    return found.text.strip() if found is not None and found.text else default


def parse_device(root):
    device = root.find("Device")
    return {
        "hostname": get_text(device, "hostname"),
        "location": get_text(device, "Location"),
        "vendor": get_text(device, "Vendor"),
    }


def parse_interfaces(root):
    interfaces = []
    # root.iter("Interfaces") menangkap semua <Interfaces> di dalam setiap <Interface>
    for intf in root.iter("Interfaces"):
        interfaces.append({
            "name": get_text(intf, "Name"),
            "description": get_text(intf, "Description"),
            "ip": get_text(intf, "IPAddress"),
            "mask": get_text(intf, "Subnetmask"),
            "status": get_text(intf, "Status"),
        })
    return interfaces


def parse_static_routes(root):
    routes = []
    for r in root.findall("./Routing/StaticRoutes/Routes"):
        routes.append({
            "destination": get_text(r, "Destination"),
            "mask": get_text(r, "Mask"),
            "next_hop": get_text(r, "NextHop"),
        })
    return routes


def parse_ospf(root):
    ospf = root.find("./Routing/OSPF")
    if ospf is None:
        return None
    networks = []
    for n in ospf.findall("./Networks/Network"):
        networks.append({
            "ip": get_text(n, "IP"),
            "wildcard": get_text(n, "Wildcard"),
            "area": get_text(n, "Area"),
        })
    return {
        "process_id": get_text(ospf, "ProcessID"),
        "router_id": get_text(ospf, "RouterID"),
        "networks": networks,
    }


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "device.xml"

    try:
        root = ET.parse(filename).getroot()
    except FileNotFoundError:
        sys.exit(f"Error: file '{filename}' tidak ditemukan.")
    except ET.ParseError as e:
        sys.exit(f"Error: XML tidak valid -> {e}")

    device = parse_device(root)
    interfaces = parse_interfaces(root)
    routes = parse_static_routes(root)
    ospf = parse_ospf(root)

    print("=== DEVICE ===")
    print(f"Hostname : {device['hostname']}")
    print(f"Location : {device['location']}")
    print(f"Vendor   : {device['vendor']}")

    print("\n=== INTERFACES ===")
    for i in interfaces:
        print(f"{i['name']} ({i['description']})")
        print(f"  IP      : {i['ip']}")
        print(f"  Mask    : {i['mask']}")
        print(f"  Status  : {i['status']}")

    print("\n=== STATIC ROUTES ===")
    for r in routes:
        print(f"{r['destination']} {r['mask']} via {r['next_hop']}")

    print("\n=== OSPF ===")
    if ospf:
        print(f"Process ID : {ospf['process_id']}")
        print(f"Router ID  : {ospf['router_id']}")
        for n in ospf["networks"]:
            print(f"  network {n['ip']} {n['wildcard']} area {n['area']}")
    else:
        print("Tidak ada konfigurasi OSPF.")


if __name__ == "__main__":
    main()
