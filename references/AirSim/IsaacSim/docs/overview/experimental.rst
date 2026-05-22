Core Experimental API
#####################

.. hint::

    At this time, the Core Experimental API is considered, as its name suggests, experimental and it is under development.
    Going forward, it will become the base API used in all Isaac Sim source code.
    The current Core API will be deprecated and removed in future releases. 

    Therefore, **we strongly encourage early adoption and use of the Core Experimental API.**

.. warning::

    The API featured in the ``isaacsim.core.experimental.*`` extensions is experimental and subject to change without deprecation cycles.
    Although we will try to maintain backward compatibility in the event of a change, it may not always be possible.

Overview
--------

The Core Experimental API (exposed by the ``isaacsim.core.experimental.*`` extensions)
is a rewritten implementation of the current Isaac Sim's Core API.
It is designed to be more robust, flexible, and powerful, yet still maintain the core utilities and wrapper concepts.

Main features (compared to the current Core API)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Warp-based implementation** for numeric data containers (such as arrays and tensors).

  While the current Core API operates with (user-selectable) numeric data containers
  -- NumPy arrays (CPU) or Torch tensors (CPU/GPU) --,
  the Core Experimental API operates with `Warp <https://nvidia.github.io/warp/>`_ arrays (CPU/GPU).
  
  Functions, properties and methods that operate on numeric data containers:

  * always return data as Warp array, and
  * have native support for input data presented as Python basic types (e.g.: int, float), lists, or NumPy arrays.

  |br| E.g.: for a ``RigidPrim`` instance wrapping 2 rigid bodies,
  calling the :meth:`~isaacsim.core.experimental.prims.RigidPrim.set_masses`
  and :meth:`~isaacsim.core.experimental.prims.RigidPrim.get_masses` methods
  that expect and return a Warp array respectively:

  .. code-block:: python

      >>> rb.set_masses(wp.array([5.0, 5.0]))  # expected data (Warp array)
      >>> rb.set_masses(np.array([5.0, 5.0]))  # <-- this is fine (NumPy array)
      >>> rb.set_masses([5.0, 5.0])            # <-- this is fine (Python list)
      >>> rb.set_masses(5.0)                   # <-- this is fine (Python basic type)
      >>>
      >>> output = rb.get_masses()             # 'output' is a Warp array

* **View wrappers**.

  *View* refers to the capability of a wrapper to wrap and operate on multiple USD prims.

  In contrast to the current Core API (where only some of the ``isaacsim.core.prims`` extension's wrapper
  classes allow wrapping multiple USD prims: *Articulation*, *RigidPrim*, *XFormPrim*, etc.),
  all Core Experimental API wrappers support wrapping one or more USD prims in the stage
  (not only for *Articulation*, *RigidPrim*, *XformPrim*, etc., but for shapes, meshes, lights, visual/physics materials).

  There are no single-prim wrappers (a particular case of multi-prim wrappers) in the Core Experimental API.

* **Automatic device/dtype conversion and broadcasting** for input data.

  E.g.: for a ``RigidPrim`` instance wrapping 2 rigid bodies,
  calling the :meth:`~isaacsim.core.experimental.prims.RigidPrim.set_masses` method
  that expects a Warp array with shape ``(N, 1)`` and dtype ``wp.float32``:

  * Device

    .. code-block:: python

        >>> rb.set_masses(wp.array([[5.0], [5.0]], device="cuda:0"))  # expected device
        >>> rb.set_masses(wp.array([[5.0], [5.0]], device="cuda:1"))  # <-- this is fine
        >>> rb.set_masses(wp.array([[5.0], [5.0]], device="cpu"))     # <-- this is fine

  * Dtype

    .. code-block:: python

        >>> rb.set_masses(wp.array([[5.0], [5.0]], dtype=wp.float32))  # expected dtype
        >>> rb.set_masses(wp.array([[5], [5]], dtype=wp.uint8))        # <-- this is fine
        >>> rb.set_masses(wp.array([[5], [5]]))  # <-- this is fine (int64, implicit)
        >>> rb.set_masses(5)                     # <-- this is fine (int, implicit)

  * Broadcasting (following `NumPy's broadcasting rules <https://numpy.org/doc/stable/user/basics.broadcasting.html>`_)

    .. code-block:: python

        >>> rb.set_masses(wp.array([[5.0], [5.0]]))  # expected shape
        >>> rb.set_masses(wp.array([5.0, 5.0]))      # <-- this is fine
        >>> rb.set_masses(wp.array([5.0]))  # <-- this is fine (same value for all prims)
        >>> rb.set_masses(5.0)              # <-- this is fine (same value for all prims)

* **Backend selection** with fallback mechanism.

  See :ref:`backend-specification`.


Motivation behind its design and implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Reduce Isaac Sim's third-party dependencies and package size.

  As the Core Experimental API becomes the main Core API in future releases, PyTorch will no longer be a dependency.
  This will reduce the size of the Isaac Sim distributions (~ 4 GB).

* Simplify the Core API implementation and boost its maintainability.

* Streamline the integration of other Deep/Machine Learning frameworks (e.g., PyTorch, JAX, TensorFlow) and libraries.

  Although the Core Experimental API is implemented using Warp, it can
  `interoperate <https://nvidia.github.io/warp/modules/interoperability.html>`_
  with other frameworks through standard interface protocols for exchanging data in a zero-copy manner.

  See the Isaac Sim's standalone example (``standalone_examples/api/isaacsim.core.experimental``)
  for a demonstration of how the Core Experimental API integrates with PyTorch, JAX, NumPy, and Warp itself.

  .. caution::

    Although interoperability is possible with the current Core API, it can become challenging.

    As a case, there is a dependency conflict between PyTorch 2.7.0 (an explicit requirement/dependency of Isaac Sim)
    and JAX versions 0.6 and higher. Additionally, having both frameworks active leads to excessive resource
    consumption and GPU memory allocation.

.. _backend-specification:

Backends
--------

The Experimental Core API is implemented using one or more of the backends listed in the following table.
The docstring of the API's functions, properties and methods indicates which backends are supported (in order of call).

.. |OpenUSD| replace:: `OpenUSD <https://www.nvidia.com/en-us/omniverse/usd>`__
.. |IFabricHierarchy| replace:: `Fabric Scene Delegate (FSD) and IFabricHierarchy <https://docs.omniverse.nvidia.com/kit/docs/usdrt/latest/docs/fabric_hierarchy.html>`__
.. |Fabric| replace:: `USD, Fabric, and USDRT <https://docs.omniverse.nvidia.com/kit/docs/usdrt/latest/docs/usd_fabric_usdrt.html>`__
.. |Omni Physics Tensors| replace:: `Omni Physics Tensors <https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/extensions/runtime/source/omni.physics.tensors/docs/index.html>`__

.. list-table::
    :header-rows: 1

    * - Backend
      - Description
      - Performance
      - Availability
    * - :guilabel:`usd`
      - System for authoring, composing, and reading hierarchically organized scene description (see |OpenUSD|).
        OpenUSD is foundational to NVIDIA Omniverse.
      - Standard
      - At any time
    * - :guilabel:`usdrt`
      - Omniverse API that mirrors the USD API but reads and writes data to and from Fabric instead of USD (see |IFabricHierarchy|).
      - Fast
      - At any time
    * - :guilabel:`fabric`
      - Omniverse library that enables high-performance creation, modification, and access of scene data (see |Fabric|).
      - Fast
      - At any time
    * - :guilabel:`tensor`
      - Interface for interacting with physics simulations in a data-oriented way (see |Omni Physics Tensors|).
      - Fastest
      - During simulation

.. warning::

    The :guilabel:`usdrt` and :guilabel:`fabric` backends require Fabric Scene Delegate (FSD) to be enabled.
    FSD can be enabled in *apps/.kit* experience files by setting ``app.useFabricSceneDelegate = true``.

.. warning::

    The :guilabel:`tensor` backend requires the simulation to be running (in play). Calling a property or method
    implemented only using this backend will raise an :exc:`AssertionError` if the simulation is not running.
    If the implementation supports several backends, and the simulation is not running, the call will fallback
    to the next listed backend (typically :guilabel:`usd`).

Backend selection
^^^^^^^^^^^^^^^^^

The selection of a backend (when an implementation supports more than one) will be made according to its
*availability* and according to the listed order. The *availability* refers to the state of the simulation
in which a backend can be used after instantiating a class.

A specific backend can be explicitly requested using the :func:`~isaacsim.core.experimental.utils.impl.backend.use_backend` context manager.

.. warning::

    If a backend is explicitly requested (using the :func:`~isaacsim.core.experimental.utils.impl.backend.use_backend` context manager)
    but is unavailable at the time of the request, resulting in a fallback to another backend, a warning is logged.

Authoring/querying visibility relationship
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. raw:: html

    <style type="text/css">
        .backends-table {
            min-width: 75%;
        }
        .backends-table td {
            border-color: gray;
            border-style: solid;
            border-width: 1px;
        }
        .backends-table p {
            margin: 0;
            padding: 0;
        }
        .backends-table .corner-cell {
            border-top: none;
            border-left: none;
        }
        .center {
            text-align: center;
            vertical-align: middle;
        }
    </style>
    <table class="backends-table">
    <caption>
        <p>Data authoring (set) and querying (get) visibility relationship between</p>
        <p>the different backends for implementations that support multiple ones.</p>
    </caption>
    <tbody>
      <tr>
        <td colspan="2" rowspan="2" class="corner-cell"></td>
        <td colspan="5" class="center"><strong>Querying backend</strong></td>
      </tr>
      <tr>
        <td class="center"><span class="guilabel">usd</span></td>
        <td class="center"><span class="guilabel">usdrt</span>/<span class="guilabel">fabric</span></td>
        <td class="center"><span class="guilabel">tensor</span></td>
      </tr>
      <tr>
        <td rowspan="3" class="center"><p><strong>&nbsp;Authoring&nbsp;</strong></p><p><strong>&nbsp;backend&nbsp;</strong></p></td>
        <td><span class="guilabel">usd</span></td>
        <td class="center">all</td>
        <td class="center">all</td>
        <td class="center">all</td>
      </tr>
      <tr>
        <td><span class="guilabel">usdrt</span>/<span class="guilabel">fabric</span></td>
        <td class="center"></td>
        <td class="center">all</td>
        <td class="center">all<sup>&nbsp;(1)</sup></td>
      </tr>
      <tr>
        <td><span class="guilabel">tensor</span></td>
        <td class="center"></td>
        <td class="center">partial<sup>&nbsp;(2)</sup></td>
        <td class="center">all</td>
      </tr>
    </tbody></table>

|br| Notes:

:sup:`(1)` For the :guilabel:`tensor` backend, changes authored using the :guilabel:`usdrt` / :guilabel:`fabric`
backends will be processed when the next physics update is executed (delayed).
Therefore, querying the value immediately using this backend will not return the authored value.

:sup:`(2)` For the :guilabel:`usdrt` / :guilabel:`fabric` backends, only transform (position, orientation and scale)
and velocity changes authored using the :guilabel:`tensor` backend will be visible in such backends
after the simulation is stepped (and if the ``omni.physx.fabric`` extension is enabled).
