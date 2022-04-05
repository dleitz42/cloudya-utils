# Cloudya Utils

This project is a set of python methods for Cloudya to automate configuration workflows instead of clicking through the products web ui.

Cloudya is a cloud based PBX product provided by the german company NFON.

* Product Webpage: https://www.nfon.com/en/products/cloudya
* Wikipedia: https://en.wikipedia.org/wiki/Nfon

## Requirements

1. Python 3
1. Python 3 Packages: pyyaml, requests


## Functions

### Automate callforwardings

#### Write you own script

```
#!/usr/bin/env python3
from cloudya import Cloudya
cloudya = Cloudya(auth_user='foo@bar.com', auth_pass='secret')
cloudya.setup_cfp(cfp_alias='Foo', cfp_number=1, cfp_phonenumber='+49891234567')
```

#### Use existing script [update_cfp.py](update_cfp.py)

1. Clone file [config.yaml.dist](config.yaml.dist) to `config.yaml`
1. Update parameters in `config.yaml` to yours
1. Execute [update_cfp.py](update_cfp.py)

```
$ ./update_cfp.py
2022-04-05 01:42:26,102 INFO Login successful
2022-04-05 01:42:26,558 INFO Callforwards profile list analysed
2022-04-05 01:42:26,558 INFO Currently Active: Profile #0, Name "default", Phone "None"
2022-04-05 01:42:26,817 INFO Callforwards profile added
2022-04-05 01:42:27,046 INFO Phonenumber created
2022-04-05 01:42:27,446 INFO Phonenumber added to cfp
2022-04-05 01:42:27,724 INFO Callforwards profile 12345 activated
2022-04-05 01:42:27,997 INFO Callforwards profile list analysed
2022-04-05 01:42:27,998 INFO Currently Active: Profile #1, Name "Foo", Phone "+49 89 1234567"
2022-04-05 01:42:28,228 INFO Logout successful
```

## License

This project is licensed under GNU General Public License v3.0

For details see [LICENSE](LICENSE).
