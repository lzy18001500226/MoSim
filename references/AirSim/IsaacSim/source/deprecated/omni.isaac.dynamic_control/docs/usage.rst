Basic Usage
===========

Start physics simulation, at least one frame of simulation must occur before the Dynamic Control interface will become fully active. 

.. code-block:: python
    :linenos:

    import omni
    omni.timeline.get_timeline_interface().play()

Acquire the Dynamic Control interface and interact with an articulation. 
The code block below assumes a Franka Emika Panda robot is in the stage with a base path of ``/Franka``

.. code-block:: python
    :linenos:

    from omni.isaac.dynamic_control import _dynamic_control
    dc = _dynamic_control.acquire_dynamic_control_interface()
    
    # Get a handle to the Franka articulation
    # This handle will automatically update if simulation is stopped and restarted
    art = dc.get_articulation("/Franka")
    
    # Get information about the structure of the articulation
    num_joints = dc.get_articulation_joint_count(art)
    num_dofs = dc.get_articulation_dof_count(art)
    num_bodies = dc.get_articulation_body_count(art)
    
    # Get a specific degree of freedom on an articulation
    dof_ptr = dc.find_articulation_dof(art, "panda_joint2")

    dof_state = dc.get_dof_state(dof_ptr)
    # print position for the degree of freedom
    print(dof_state.pos)

    # This should be called each frame of simulation if state on the articulation is being changed.
    dc.wake_up_articulation(art)
    dc.set_dof_position_target(dof_ptr, -1.5)
