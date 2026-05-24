==========================================================================
Use Python Client to Communicate with Binary
==========================================================================

In a typical scenario, you have a Binary file simulating your unreal world. At the same time, you have an external Python program that wants to communicate with the simulation, send commands to control objects and characters, and get information about the world.

UnreaclCV provides a Python client to allow you communicate with Binary via:

1. TCP/IP (Windows, Mac, Linux)

2. UDS (Linux/Unix)

TCP/IP
============

TCP/IP supports cross-platform and cross-machine communication.

Following is a simple expample on TCP/IP communication.

.. code:: Python

    # 1. config the Binary listening ip and port to ('127.0.0.1', 9000)
    # 2. start the Binary

    # 3. build connection from external Python Program
    from unrealcv import Client
    (ip, port) = ('127.0.0.1', 9000)
    client = Client((ip, port), 'inet')

    def check_connection(client):
        while client.isconnected() is False:
            print('Try connecting again...')
            client.connect()
            time.sleep(1)
        else:
            print('INet Connection Established!')

    check_connection(client)
    print(client.request('vget /unrealcv/status'))


UDS (Linux)
============

UDS, short for Unix Domain Socket, provides a faster and more stable inter-process communication. `UnrealCV 4.27-stable` supports this kind of communication on linux (Unix) platforms.

`Requirement:` Binary and external Python program are running on the same machine. Unrealcv version == `4.27-stable`.

`How:`

1. Connect with Binary via TCP/IP with (ip, port).

2. Disconnect TCP/IP connection. Once disconnected, your Binary will automatically create an identifier file named by the TCP/IP port number at `/tmp/unrealcv_{port}.socket`.

3. Connect to `/tmp/unrealcv_{port}.socket` via UDS.

.. code:: Python

    # Connect over TCP on first connection
    from unrealcv import Client
    import os, sys
    import time

    (ip, port) = ('127.0.0.1', 9000)
    client = Client((ip, port), 'inet')

    def check_connection(client):
        while client.isconnected() is False:
            print('Try connecting again...')
            client.connect()
            time.sleep(1)
        else:
            print('INet Connection Established!')

    check_connection(client)

    # Try switching to UDS
    if 'linux' in sys.platform and unrealcv.__version__>= '1.0.0':
        unix_socket_path = f'/tmp/unrealcv_{port}.socket'
        os.remove(unix_socket_path) if os.path.exists(unix_socket_path) else pass  # clean the old socket
        client.disconnect()
        print('Disconnect Inet connection. Waiting for UDS service to start (6s)...')
        time.sleep(6)  # may be longer or shorter, depending on your machine

        if os.path.exists(unix_socket_path):
            print('Switching to UDS communication...')
            client = Client(unix_socket_path, 'unix')
            check_connection(client)
            print('UDS Communication Established')
        else:
            print('UDS service does not start. Switch back to Inet')
            check_connection(client)  # reconnect via TCP/IP

    print(client.request('vget /unrealcv/status'))


`Typical Use Case:` Parallel Machine Learning. Suppose you would like to parallelize many Binaries on a single linux server to train your deep learning agents. It is suggested to use UDS for a faster and more stable communication. In our test, UDS is able to maintain stable communication when the machine is under very high workload (e.g. running 120 `Biarnies <https://github.com/Embracing/Active3DPose/tree/main>`__ simultaneously).