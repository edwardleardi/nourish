This directory contains the TLS key and certificate for running our tests.

## Generate TLS Key and Self-Signed Certificate Using GnuTLS

The key and certificate were generated as follows:

1. Run:

       $ certtool --generate-privkey --sec-param=high --outfile server.key
       $ certtool --generate-self-signed --load-privkey server.key --outfile server.pem

2. Answer:

        Generating a self signed certificate...
        Please enter the details of the certificate's distinguished name. Just press enter to ignore a field.
        Common name: localhost
        UID: 
        Organizational unit name: 
        Organization name: Nourish
        Locality name: San Francisco
        State or province name: CA
        Country name (2 chars): US
        Enter the subject's domain component (DC): 
        This field should not be used in new certificates.
        E-mail: 
        Enter the certificate's serial number in decimal (default: 6935566551012165747): 


        Activation/Expiration time.
        The certificate will expire in (days): 999999


        Extensions.
        Does the certificate belong to an authority? (y/N): y
        Path length constraint (decimal, -1 for no constraint): 
        Is this a TLS web client certificate? (y/N): 
        Will the certificate be used for IPsec IKE operations? (y/N): 
        Is this a TLS web server certificate? (y/N): y
        Enter a dnsName of the subject of the certificate: localhost
        Enter a dnsName of the subject of the certificate: 
        Enter a URI of the subject of the certificate: 
        Enter the IP address of the subject of the certificate: 127.0.0.1
        Will the certificate be used for signing (DHE ciphersuites)? (Y/n): 
        Will the certificate be used for encryption (RSA ciphersuites)? (Y/n): 
        Will the certificate be used to sign OCSP requests? (y/N): 
        Will the certificate be used to sign code? (y/N): 
        Will the certificate be used for time stamping? (y/N): 
        Will the certificate be used for email protection? (y/N): 
        Will the certificate be used to sign other certificates? (y/N): y
        Will the certificate be used to sign CRLs? (y/N): 
        Enter the URI of the CRL distribution point: 
        X.509 Certificate Information:
                Version: 3
                Serial Number (hex): 604015082d294873
                Validity:
                        Not Before: Wed Mar 03 23:00:32 UTC 2021
                        Not After: Wed Jan 28 23:00:50 UTC 4759
                Subject: C=US,ST=CA,L=San Francisco,O=Nourish,CN=localhost
                Subject Public Key Algorithm: RSA
                Algorithm Security Level: High (3072 bits)
                        Modulus (bits 3072):
                                00:96:c4:15:34:16:fd:da:f4:bf:76:de:a7:03:db:7c
                                6e:75:81:c5:02:fb:2d:e6:04:a3:cb:3b:0f:a2:11:9e
                                82:a5:90:3e:90:e3:01:83:b4:e4:72:d0:5e:39:12:40
                                f3:79:40:a9:71:0d:72:09:95:39:33:83:db:57:fd:eb
                                b2:8b:a1:d7:34:b7:2c:c8:0c:da:0a:ea:16:59:01:1c
                                7f:c2:3c:93:bb:55:4e:62:b5:e6:20:d0:cd:fe:48:4c
                                a7:08:cb:8b:11:74:1e:93:c6:4c:96:ac:3e:4f:34:16
                                3e:6d:c2:5f:37:ba:cc:0e:af:27:67:fc:3a:93:5f:a6
                                1c:34:9e:99:05:d6:53:d2:cb:42:66:03:99:3e:2f:e2
                                aa:08:bb:e4:43:a7:19:d5:94:9c:b8:54:ba:e2:31:0b
                                fc:29:c5:02:59:b9:da:65:7a:c8:4a:f6:9a:9a:ee:93
                                3b:f0:23:97:7b:36:9c:9b:ae:20:e9:d6:7d:37:b0:23
                                c6:ff:73:dd:9c:5f:5d:c0:e1:1e:f9:8a:33:e1:17:45
                                fa:ea:7d:22:84:52:b4:28:58:2a:77:41:04:84:5f:14
                                52:e4:73:53:1f:96:ec:1d:27:c9:81:6a:31:e0:69:89
                                d2:1d:8c:0c:04:78:ea:c2:51:43:cd:fc:f0:fe:60:55
                                24:b4:30:53:7a:4b:1b:29:c7:33:9f:d4:6b:b5:d0:a9
                                a2:71:8e:09:f6:76:8a:82:c1:5b:97:76:46:87:55:87
                                ee:d2:ba:22:e4:93:3d:9e:a6:52:34:a9:3a:60:f8:1e
                                06:fd:63:0c:f4:b2:9f:d8:50:51:cb:7e:d5:82:e7:04
                                f3:d0:3c:f2:4a:45:bc:29:1b:e9:fc:1d:2e:05:7b:9c
                                fe:b0:be:92:e2:72:94:a2:1b:68:f6:ab:38:7a:19:5f
                                9d:73:74:23:72:7d:f5:e4:9c:41:72:4f:c9:d1:86:d8
                                4c:11:1f:02:4e:78:89:62:9e:b1:e7:67:84:3b:d1:fb
                                f9
                        Exponent (bits 24):
                                01:00:01
                Extensions:
                        Basic Constraints (critical):
                                Certificate Authority (CA): TRUE
                        Subject Alternative Name (not critical):
                                DNSname: localhost
                                IPAddress: 127.0.0.1
                        Key Purpose (not critical):
                                TLS WWW Server.
                        Key Usage (critical):
                                Digital signature.
                                Key encipherment.
                                Certificate signing.
                        Subject Key Identifier (not critical):
                                c760c2bf6d3f89e4a7e0a96f57ab15d7cbad5df7
        Other Information:
                Public Key ID:
                        sha1:c760c2bf6d3f89e4a7e0a96f57ab15d7cbad5df7
                        sha256:f96852af7022dcd462f7e14b2c4a6fa924d3634b93ecc1574991356d35ad7dff
                Public Key PIN:
                        pin-sha256:+WhSr3Ai3NRi9+FLLEpvqSTTY0uT7MFXSZE1bTWtff8=
                Public key's random art:
                        +--[ RSA 3072]----+
                        |                 |
                        |     .           |
                        |      o o        |
                        |       + o     . |
                        |        S o . . .|
                        |         +. .o. o|
                        |        oooo.o o+|
                        |       ..++o=  o+|
                        |      .++.o+... E|
                        +-----------------+

        Is the above information ok? (y/N): y

Reference: https://help.ubuntu.com/community/GnuTLS#Self-Signing
