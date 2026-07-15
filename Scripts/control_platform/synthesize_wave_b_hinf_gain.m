function synthesize_wave_b_hinf_gain(upstream_dir, output_path)
% Freeze the licensed upstream H-infinity controller at the hover operating point.

addpath(upstream_dir);

mass = 1.0;
gravity = 9.8;
inertia_x = 0.01466;
inertia_y = 0.01466;
inertia_z = 0.02848;

% State order follows the upstream simulator:
% roll, pitch, yaw, p, q, r, u, v, w, x, y, z.
A = zeros(12, 12);
A(1, 4) = 1.0;
A(2, 5) = 1.0;
A(3, 6) = 1.0;
A(7, 2) = -gravity;
A(8, 1) = gravity;
A(10, 7) = 1.0;
A(11, 8) = 1.0;
A(12, 9) = 1.0;

B1 = zeros(12, 6);
B1(4, 4) = 1.0 / inertia_x;
B1(5, 5) = 1.0 / inertia_y;
B1(6, 6) = 1.0 / inertia_z;
B1(7, 1) = 1.0 / mass;
B1(8, 2) = 1.0 / mass;
B1(9, 3) = 1.0 / mass;

B2 = zeros(12, 4);
B2(4, 2) = 1.0 / inertia_x;
B2(5, 3) = 1.0 / inertia_y;
B2(6, 4) = 1.0 / inertia_z;
B2(9, 1) = -1.0 / mass;

C1 = zeros(14, 12);
C1(1, 3) = 125.0;
C1(2, 4) = 10.0;
C1(3, 5) = 10.0;
C1(4, 6) = 25.0;
C1(5, 7) = 50.0;
C1(6, 8) = 50.0;
C1(7, 9) = 100.0;
C1(8, 10) = 200.0;
C1(9, 11) = 200.0;
C1(10, 12) = 160.0;

[gamma, gamma_lb, X, riccati_residual] = hinf_syn(A, B1, B2, C1, 0);
K = -B2.' * X;
closed_loop_eigenvalues = eig(A + B2 * K);

payload = struct();
payload.schema = 'mosim.control_platform.hinf_frozen_gain.v1';
payload.upstream_commit = 'fd51f68701ec1bd549b9796d8277db2c8fb89240';
payload.operating_point = 'hover_zero_euler_zero_body_velocity';
payload.state_order = {'roll', 'pitch', 'yaw', 'p', 'q', 'r', ...
    'u', 'v', 'w', 'x', 'y', 'z'};
payload.command_order = {'collective_force_ned', 'tau_x', 'tau_y', 'tau_z'};
payload.gamma = gamma;
payload.gamma_lower_bound = gamma_lb;
payload.riccati_residual = riccati_residual;
payload.max_closed_loop_real_eigenvalue = max(real(closed_loop_eigenvalues));
payload.gain = K;
payload.source_runtime_recomputed = false;
payload.claim_ceiling = ['Licensed upstream synthesis reproduced at one frozen hover ', ...
    'operating point; this is not a nonlinear, MWORKS, generated-C, or runtime acceptance.'];

fid = fopen(output_path, 'w');
assert(fid >= 0, 'Cannot open output file: %s', output_path);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', jsonencode(payload, PrettyPrint=true));
end
