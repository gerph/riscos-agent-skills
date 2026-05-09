# Networking status and enumeration services

## What they are used for

Networking modules use service calls to track DCI driver/protocol availability, Internet interface state, Freeway lifecycle, PPP driver state, and statistics enumeration.

Relevant PRM context: <http://www.riscos.com/support/developers/prm/internet.html>, section "Service calls".

Common services:

- `Service_DCIProtocolStatus`: protocol module started/dying.
- `Service_DCIDriverStatus`: driver started, link active, link inactive, or driver dying.
- `Service_InternetStatus`: interface address changes, dynamic boot replies, duplicate IP warnings.
- `Service_InternetVars`: Internet variables or configuration became available/changed.
- `Service_StatisticEnumerate`: append module statistics to a DCI statistics list.
- `Service_EnumerateNetworkDrivers`: enumerate DCI/PPP drivers.
- `Service_GenericPPPState`: GenericPPP module/device lifecycle.
- `Service_FreewayStarting`, `Service_FreewayTerminating`: Freeway service lifecycle.

## CMHG form

DHCPClient listens to the normal DCI/Internet set:

```cmhg
service-call-handler: Mod_Service Service_DCIProtocolStatus,
                                  Service_DCIDriverStatus,
                                  Service_InternetStatus,
                                  Service_StatisticEnumerate
```

GenericPPP is both a network driver provider and a consumer of protocol/driver state:

```cmhg
service-call-handler: Mod_Service Service_EnumerateNetworkDrivers,
                                  Service_DCIDriverStatus,
                                  Service_DCIProtocolStatus
```

PPPoE and PPPoTCP listen for GenericPPP state:

```cmhg
service-call-handler: Mod_Service Service_GenericPPPState
```

RemotePrinterSupport uses numeric Freeway services:

```cmhg
service-call-handler: sc_handler &95 &96
```

## C usage

DHCPClient uses `Service_InternetStatus` sub-reasons in `r0`:

```c
case Service_InternetStatus:
    switch (r->r[0])
    {
        case InternetStatus_AddressChanged:
            dhcp_addresschanged((const char *)r->r[2], (void *)r->r[3]);
            break;

        case InternetStatus_DynamicBootReply:
            dhcp_gotreply((const char *)r->r[2], (void *)r->r[3],
                          (unsigned char *)r->r[4], r->r[5]);
            break;

        case InternetStatus_DuplicateIPAddress:
            if (dhcp_duplicateip(...))
                r->r[1] = Service_Serviced;
            break;
    }
    break;
```

`Service_DCIProtocolStatus` (`&9F`) uses `r0` as the protocol module private word pointer, `r2` as status, `r3` as DCI version supported times 100, and `r4` as a pointer to the protocol module title string. The PRM defines status zero as starting and one as terminating. DHCP only reacts to the `"Internet"` protocol, waking on `DCIProtocolStatus_Started` and sleeping on `DCIProtocolStatus_Dying`. Preserve `r0` to `r4` and do not claim. A terminating protocol must continue handling receive events for frame types it has not relinquished until this service returns.

`Service_DCIDriverStatus` (`&9D`) passes a DIB pointer in `r0`, a status in `r2`, and the DCI version supported times 100 in `r3`. The PRM defines status zero as starting and one as terminating. DHCP builds an interface name from `dib_name` and `dib_unit`, then marks the interface active/inactive for link status changes used by the newer sources. Preserve `r0` to `r3` and do not claim. If keeping a terminating driver on a list for possible restart, match it by short name and unit number rather than by the DIB address, because a restarted module may allocate its DIB at a different address.

`Service_StatisticEnumerate` is an append-to-list interface. DHCP casts `r0` to a statistics-control pointer list and appends its statistics:

```c
case Service_StatisticEnumerate:
    stats_enumerate((dci4_spctl **)&r->r[0]);
    break;
```

`Service_EnumerateNetworkDrivers` returns an updated chain head in `r0`:

```c
case Service_EnumerateNetworkDrivers:
    r->r[0] = (int)ifdriver_enumerateall((ChDib *)r->r[0]);
    break;
```

The PRM defines `Service_EnumerateNetworkDrivers` (`&9B`) as an RMA-allocated transient linked list. On entry, `r0` is the current head, initially null. A driver should chain one entry per logical interface at the head of the list. Each entry contains a next pointer at offset 0 and a pointer to a static driver information block at offset 4. The issuer frees the transient entries after the service returns. Preserve `r1` and do not claim.

The PRM documents `Service_InternetStatus` (`&B0`) subreason zero as address changed after a successful `SIOCSIFADDR` `socketioctl()`. It says to preserve `r0` and `r1` and not claim. The newer sources include additional subreasons such as dynamic boot replies and duplicate IP detection; follow the local header for those extensions.

GenericPPP also issues its own state service on startup:

```c
_swix(OS_ServiceCall, _INR(0,1),
      Service_GenericPPPState_ModuleAlive,
      Service_GenericPPPState);
```

PPPoE listens for `Service_GenericPPPState` sub-reasons in `r0`, shutting down all sessions when GenericPPP dies and destroying sessions whose PPP device died.

## Related information

Networking services mix notifications and claimable conflict-resolution calls. Address-duplicate handling and device acceptance may claim; plain started/dying/link-state notifications should normally be left unclaimed.
