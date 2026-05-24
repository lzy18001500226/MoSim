Pytorch Online Writer and Listener
==================================

The ``PytorchWriter`` and ``PytorchListener`` are APIs for using ``omni.replicator``'s writer API to retrieve 
various data such as RGB from the specified cameras (supports multiple cameras) and provides them to 
the user in both default format (e.g.: PNG for RGB data) and batched pytorch tensors. The ``PytorchListener`` 
provides an API to directly retrieve data sent to the ``PytorchWriter`` without the need to access the stored 
by ``omni.replicator``'s ``BackendDispatch``.
