# cases.csv Schema

The `cases.csv` file acts as the source-of-truth dataset for NetSage AI. It should contain exactly 12 columns in a strict, comma-separated format.

## Columns Definition

| Column | Type | Description | Example |
|---|---|---|---|
| `case_id` | String | Unique identifier for the case | `C-001` |
| `title` | String | A short descriptive title of the issue | `PC cannot reach gateway due to wrong VLAN` |
| `category` | String | The category of the issue. **Must be one of the allowed values.** | `VLAN` |
| `symptom` | String | What the user initially experiences | `PC fails to ping default gateway 192.168.1.1` |
| `topology_note` | String | Context about the physical / logical topology | `PC connected to SW1 port Fa0/1` |
| `show_outputs` | String (multi-line) | Realistic Cisco `show` command output. Must be robustly escaped/quoted in CSV | `"SW1# show vlan brief\n..."` |
| `expected_fault` | String | The true root cause of the issue | `PC is in VLAN 1 but should be in VLAN 10` |
| `osi_layer` | Integer/String | The OSI layer where the fault occurs (integer mostly) | `2` |
| `concept` | String | Network concept being tested | `VLAN basics` |
| `severity` | String | Example: low, medium, high | `low` |
| `expected_next_command` | String | The command a normal engineer would run next to verify | `show interface Fa0/1 switchport` |
| `expected_fix` | String | How to fix it | `switchport access vlan 10` |

## Allowed Categories
The `category` column MUST be one of the following exact strings:
- `VLAN`
- `Gateway/IP`
- `DHCP`
- `DNS`
- `Routing`
- `ACL`
- `NAT`
- `Wireless`
