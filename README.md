# Elemento Power Meter
EPM is a set of utilities and routines to estimate the power draw of linux systems.
Typically the set of dependencies is intended to be as small as possible.
We are trying to stick as much as possible to built in tols and routines.


## CPU power
We pursued two approaches which are equivalent.
Both are aimed at getting the CPU energy integral in two moments spread by 0.5s.
The power is computed via the following pseudocode:

```
t0_energy=read_energy()
wait for 0.5s
t1_energy=read_energy()

power=(t1_energy - t0_energy)/0.5
```

> **Warning**
> EPM currently supports only single-socket systems. Multi socket support should be easily supported by iterating over the socket indexes.

### Via `lm_sensors`
It requires installing the `lm_sensors` package [link](https://wiki.archlinux.org/title/lm_sensors).

After installation a sensors detection is required through `sensors detect`.
The values are returned in Joules and handled accordingly.

See [the implementation here](./cpu-power.sh).

### Via `sysfs` and `intel-rapl`
It uses `intel-rapl` intefraces through `sysfs` [link](https://web.eece.maine.edu/~vweaver/projects/rapl/).

It works out of the box, returning values in uJoules.

See [the implementation here](./cpu-rapl-power.sh).


## RAM power
RAM power consumption is not depending on the RAM load, but rather on the techology.
As a reference, here are the typical consumptions for RAM modules on different DDR versions:

| **Type** | **Voltage** | **Power draw** |
|:--------:|:-----------:|:--------------:|
| DDR1     | 2.5V        | 5.5W           |
| DDR2     | 1.8V        | 4.5W           |
| DDR3     | 1.5V        | 3W             |
| DDR4     | 1.2V        | 3W             |
| DDR5     | 1.1V        | 2.4W           |

(from [link](https://www.buildcomputers.net/power-consumption-of-pc-components.html))

Since every stick of ECC memory has an additional memory chip for parity every 8 chips, we sum and additional 12.5% to the reference value for ECC sticks.

The RAM power draw is fixed and is not changing in time in our approach.

We use a mix of `strace` and `dmidecode` routines to detect the number of RAM sticks and the presence of ECC technologies.
See [the implementation here](./ram-power.sh).

The value is not updating and is therefore a fixed value depending on hardware configuration and not on runtime information.

## NVMe power
NVMe power consuption is mainly dependant on the NVMe device power state.
According to [the NVMexpress consortium](https://nvmexpress.org/resources/nvm-express-technology-features/nvme-technology-power-features/) the reference rating for different power states are:

| **Power state** | **Max power draw** |
|:---------------:|:------------------:|
| 0               | 25W                |
| 1               | 18W                |
| 2               | 18W                |
| 3               | 15W                |
| 4               | 10W                |
| 5               | 8W                 |
| 6               | 5W                 |

However, the `smartctl` command is able to return the specific ratings for an nvme device.
It can be used via `smartctl -a /dev/nvmeXX` under the header "`Supported Power States`".
For example:

```
Supported Power States
St Op     Max   Active     Idle   RL RT WL WT  Ent_Lat  Ex_Lat
 0 +     8.25W    8.25W       -    0  0  0  0        0       0
 1 +     3.50W    3.50W       -    0  0  0  0        0       0
 2 +     2.60W    2.60W       -    0  0  0  0        0       0
 3 -   0.0250W       -        -    3  3  3  3     5000   10000
 4 -   0.0050W       -        -    4  4  4  4     3900   45700
```

Such information in parsed and used in the consumption computation.

The current power state is retrieved through `nvme get-feature /dev/nvmeXX -f 2 -H`, which return a value corresponding to the above table.
In addition the disk activity state is parsed via `hdparm`. The returned state values are `unknown`, `active/idle`, `standby` and `sleep`.

> **Warning**
> `hdparm` often causes an asleep disk or a standby disk to spin up/go to a higher power state. This has been shown to cause an increase of power consumption during readout. The storage part of EPM should be ran at low rate!

If `unknown` or `active/idle`, further information about disk activity is gotten via `/sys/block/nvmeXX/stat` reading it twice in a row with minimum delay (0.1s) and comparing the outputs.
By doing so it is possible to further correct the nominal power consumptions using the following table:

| **Power state**                    | **Coefficient** |
|:----------------------------------:|:---------------:|
| `unknown` and `sysfs` active       | 1.0             |
| `unknown` and `sysfs` inactive     | 0.2             |
| `active/idle` and `sysfs` active   | 1.0             |
| `active/idle` and `sysfs` inactive | 0.2             |
| `standby`                          | 0.2             |
| `sleeping`                         | 0.1             |

The power state can change over time, therefore this module must be considered time-variable.

## Storage power (SATA/SAS)
Our initial approach on this point is to just differentiate on wether the device is an SSD or a spinning disk (and the RPMs in case of the latter).
An upgrade is related to check disk activity, but for the moment we decided to just keep the upper limit of power consumption.

Data have been obtained from varoius sources. The following table reports the adopted standard values:
| **Drive type**  | **Max power draw** |
|:---------------:|:------------------:|
| SSD             | 4.2W               |
| 15k RPM HDD     | 6.5W               |
| 10k RPM HDD     | 5.8W               |
| 7.2k RPM HDD    | 8W                 |

Devices enumeration is done using `lsscsi`, while the rated RPM/solid stateness is obtained looking into `sg_vpd`.
Disk activity is then estimated at first by looking into `sysfs` at `/sys/block/sdXX/stat` twice in a row with minimum delay (0.1s) and comparing the outputs.
If no activity is detected via `sysfs`, the specific inactive state is gotten from `smartctl`.


| **Power state**                    | **Coefficient** |
|:----------------------------------:|:---------------:|
| `unknown` and `sysfs` active       | 1.0             |
| `unknown` and `sysfs` inactive     | 0.2             |
| `active/idle` and `sysfs` active   | 1.0             |
| `active/idle` and `sysfs` inactive | 0.2             |
| `standby`                          | 0.2             |
| `sleeping`                         | 0.1             |

The power state can change over time, therefore this module must be considered time-variable.

## NIC power
For what concerns network devices we got some hints from this article: [Characterizing 10 Gbps Network Interface Energy Consumption](https://www.cl.cam.ac.uk/~acr31/pubs/sohan-10gbpower.pdf).
The findings of the authors are quite interesting and tend to support a Gbps/W invariance across multiple NIC models.
We then followed their approach, adding some kind of modulation dependant of the medium (DAC, Fiber, Base-T) and on the max speed of the adapter.

For every NIC in the system we retrieve the following info:
* Current speed: in Mbps
* Transceiver: `internal` or `external`
* Medium: namely `Twisted Pair`, `Direct Attach Copper`, `FIBRE` and more

From the cited article we got the following phenomenological values in Gbps/W:

| **Adapter maximum speed**          | **Power coefficient [Gbps/W]**      |
|:----------------------------------:|:---------------:|
| 100Mbps                            | 0.1             |
| 1Gbps                              | 0.45            |
| 10Gbps                             | 0.8             |
| >10Gbps                            | 0.9             |

The medium correction is a multiplicative factor defined as follows:

| **Medium**          | **Efficiency coefficient**      |
|:-------------------:|:-------------------------------:|
| Twisted Pair (RJ45) | 1.                              |
| DAC                 | 3.5                             |
| Fiber               | 2.                              |

For each port the power consumption is the computed using the following formula, where the Power Coefficient is $\sigma_{Power}$ and the Efficiency Coefficient  is $\epsilon$:

$$NIC_{power draw}=\dfrac{Speed_{Mbps}}{1000 \cdot \sigma_{Power} \cdot \epsilon}$$

The sum of all the values is taken as the total networking power consumption.
NICs with no medium connected or no active link are excluded from the computation.

Excluding for speed renegotiations this value is not updating and is therefore a fixed value (most of the times).

## PSU efficiency
Our approach is based on getting the power draw from the above methods and then using the 80Plus curves to get the load-dependent PSU efficiency.
80Plus has some well defined values for the PSU efficiencies at different loads.
In particular, the rating involves three points: 20%, 50% and 100% loads.

| **Rating**         | **20%** | **50%** | **100%** |
|:------------------:|:-------:|:-------:|:--------:|
| 80Plus             | 80%     | 80%     | 80%      |
| 80Plus Bronze      | 82%     | 85%     | 82%      |
| 80Plus Silver      | 85%     | 88%     | 85%      |
| 80Plus Gold        | 87%     | 90%     | 87%      |
| 80Plus Platinum    | 90%     | 92%     | 89%      |
| 80Plus Titanium    | 92%     | 94%     | 90%      |

We used the Kramer method to fit three points to a parabola to obtain a function of the load (defined as current poser draw divided by the maximum PSU power output).
the values are reported below, where $x$ is the percent load of the PSU and depends on a user supplied maximum power rating:

| **Rating**         | **formual** |
|:------------------:|:-----------:|
| 80Plus             | $\epsilon=80$         |
| 80Plus Bronze      | $\epsilon=-0.0354x^2+2.58x+44.571$         |
| 80Plus Silver      | $\epsilon=-0.0367x^2+2.67x+46.286$         |
| 80Plus Gold        | $\epsilon=-0.0376x^2+2.73x+47.429$         |
| 80Plus Platinum    | $\epsilon=-0.0389x^2+2.79x+49.762$         |
| 80Plus Titanium    | $\epsilon=-0.0405x^2+2.90x+52.190$         |

where `x` in the load.

This value is used as a rescaling factor to obtain the actual wall power draw from the measured power consumption.