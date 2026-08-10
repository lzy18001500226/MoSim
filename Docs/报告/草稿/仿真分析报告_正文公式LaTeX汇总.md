# 仿真分析报告正文公式 LaTeX 汇总

> 来源：`Docs/报告/草稿/仿真分析报告_正文骨架.md`。本文件只做公式提取，未改动正文。
> 显示公式保留正文原始的 `\[...\]` 定界符和 `\tag{...}`；行内公式保留原始的 `\(...\)` 定界符。
> 复制到 MathType 时，复制对应 `latex` 代码块中的内容，不要复制外围 Markdown 围栏。每条记录的章节和行号仅用于定位。

- 显示公式：108 条
- 行内公式：142 条
- 公式出现位置合计：250 条

## 一、显示公式

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 二、指标定义与负样本处理 > 2.3 参考轨迹与故障注入

#### 显示公式 001，\tag{2-1}（正文第 96-108 行）

```latex
\[
\left\{
\begin{aligned}
&x_r(t)=
\begin{cases}0,&t<20\\t-20,&20\le t<30\\10,&t\ge30\end{cases},\\
&y_r(t)=
\begin{cases}0,&t<30\\t-30,&30\le t<40\\10,&t\ge40\end{cases}.
\end{aligned}
\right.
\tag{2-1}
\]
```

#### 显示公式 002，\tag{2-2}（正文第 112-134 行）

```latex
\[
\left\{
\begin{aligned}
&z_r(t)=
\begin{cases}
2t,&0\le t<5\\
10,&5\le t<10\\
10+\frac53(t-10),&10\le t<13\\
15,&t\ge13,
\end{cases}\\
&\mathbf v_r(t)=
\begin{bmatrix}
\mathbb 1_{[20,30)}(t)\\
\mathbb 1_{[30,40)}(t)\\
2\mathbb 1_{[0,5)}(t)+\frac53\mathbb 1_{[10,13)}(t)
\end{bmatrix},\\
&\mathbf a_r(t)=\mathbf0.
\end{aligned}
\right.
\tag{2-2}
\]
```

#### 显示公式 003，\tag{2-3}（正文第 138-152 行）

```latex
\[
\left\{
\begin{aligned}
&h(t;H,T)=H\min(t/T,1),\\
&\tau=\max(0,t-5),\\
&\mathbf p_r^{hover}(t)=(0,0,h(t;2,5))^T,\\
&\mathbf p_r^{step}(t)=(\mathbb 1_{[15,\infty)}(t),-\mathbb 1_{[15,\infty)}(t),h(t;2,5))^T,\\
&\mathbf p_r^{figure8}(t)=(2\sin(0.35\tau),\sin(0.70\tau),h(t;2,5))^T,\\
&\mathbf p_r^{spiral}(t)=(1.5[\cos(0.30t)-1],1.5\sin(0.30t),0.15t)^T.
\end{aligned}
\right.
\tag{2-3}
\]
```

#### 显示公式 004，\tag{2-4}（正文第 172-185 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf F_g^W(t)=
\begin{bmatrix}0.25\\0\\0\end{bmatrix}
\mathbb 1_{[15,50)}(t)\ \mathrm N,\\
&m'=1.2m,\\
&\mathbf J'=\operatorname{diag}(1.2,1.2,1.2)\mathbf J,
\end{aligned}
\right.
\tag{2-4}
\]
```

#### 显示公式 005，\tag{2-5}（正文第 189-198 行）

```latex
\[
\eta_{f,i}(t)=
\begin{cases}
0.5,&i=1,\ t\ge15\\
1,&\text{otherwise}.
\end{cases}
\tag{2-5}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 二、指标定义与负样本处理 > 2.4 指标与有效通过判定

#### 显示公式 006，\tag{2-6}（正文第 206-217 行）

```latex
\[
\left\{
\begin{aligned}
&e_k=\lVert\mathbf p_{r,k}-\mathbf p_k\rVert_2,\\
&\mathrm{RMSE}_{p}=\sqrt{\frac{1}{N}\sum_{k=1}^{N}e_k^2},\\
&e_T=e_N .
\end{aligned}
\right.
\tag{2-6}
\]
```

#### 显示公式 007，\tag{2-7}（正文第 221-234 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf u_k=[u_{1,k},u_{2,k},u_{3,k},u_{4,k}]^T,\\
&E_{\mathrm{cmd}}=
\sum_{k=1}^{N-1}\frac{t_{k+1}-t_k}{2}
\left(\lVert\mathbf u_k\rVert_2^2+
\lVert\mathbf u_{k+1}\rVert_2^2\right).
\end{aligned}
\right.
\tag{2-7}
\]
```

#### 显示公式 008，\tag{2-8}（正文第 240-245 行）

```latex
\[
M_p=100\%\cdot\frac{\max_t|x(t)-x_{ss}|}{|x_{ss}-x(0)|}.
\tag{2-8}
\]
```

#### 显示公式 009，\tag{2-9}（正文第 250-264 行）

```latex
\[
\left\{
\begin{aligned}
&\delta_x=0.05\,|x_{tgt}-x_0|,\\
&\delta_y=0.05\,|y_{tgt}-y_0|,\\
&t_s=\min\Big\{t_k-t_0\;\Big|\;
|x(t_\ell)-x_{tgt}|\le\delta_x \;\wedge\;
|y(t_\ell)-y_{tgt}|\le\delta_y,\;
\forall t_\ell\in[t_k,t_{end}]\Big\}.
\end{aligned}
\right.
\tag{2-9}
\]
```

#### 显示公式 010，\tag{2-10}（正文第 272-283 行）

```latex
\[
\left\{
\begin{aligned}
&\mathrm{RMSE}_{tail}=
\sqrt{\frac{1}{N_{tail}}\sum_{t_k\ge t_{max}-5}e_k^2},\\
&\bar e_{ss}=\frac{1}{N_W}\sum_{t_k\ge t_{max}-\max(5,0.2t_{max})}e_k.
\end{aligned}
\right.
\tag{2-10}
\]
```

#### 显示公式 011，\tag{2-11}（正文第 287-293 行）

```latex
\[
\mathrm{pass}_{i}\leftrightarrow
\mathrm{completed}_i\ \land\ \mathrm{finite}(e_{T,i})\ \land\ e_{T,i}<5\ \mathrm{m}.
\tag{2-11}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 三、云纵150参照虚拟机体与参数 Profile > 3.1 参数分层

#### 显示公式 012，\tag{3-4a}（正文第 405-410 行）

```latex
\[
T_{body \to ray}=T_{body \to lidar\_base}\cdot T_{lidar\_base \to ray\_sensor}.
\tag{3-4a}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 三、云纵150参照虚拟机体与参数 Profile > 3.2 坐标、旋翼与物理链

#### 显示公式 013，\tag{3-6}（正文第 484-494 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf p_{NED}=\begin{bmatrix}p_{y,N}\\p_{x,E}\\-p_{z,U}\end{bmatrix},\\
&\mathbf v_{FRD}=\begin{bmatrix}v_F\\-v_L\\-v_U\end{bmatrix}.
\end{aligned}
\right.
\tag{3-6}
\]
```

#### 显示公式 014，\tag{3-7}（正文第 498-503 行）

```latex
\[
{}^{W}\mathbf v=R_{W\leftarrow B}(q)\,{}^{B}\mathbf v.
\tag{3-7}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 三、云纵150参照虚拟机体与参数 Profile > 3.3 公共动力学、执行器与实际 X 型分配

#### 显示公式 015，\tag{3-1}（正文第 519-532 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf e_p=\mathbf p_r-\mathbf p,\\
&\mathbf e_v=\mathbf v_r-\mathbf v,\\
&\dot{\mathbf p}=\mathbf v,\\
&m\dot{\mathbf v}=R_B^W\begin{bmatrix}0\\0\\T\end{bmatrix}
-mg\mathbf e_3+\mathbf d .
\end{aligned}
\right.
\tag{3-1}
\]
```

#### 显示公式 016，\tag{3-2}（正文第 536-547 行）

```latex
\[
\left\{
\begin{aligned}
&\dot R_B^W=R_B^W[\boldsymbol\omega]_\times,\\
&\mathbf J_B\dot{\boldsymbol\omega}+
\boldsymbol\omega\times(\mathbf J_B\boldsymbol\omega)=\boldsymbol\tau .
\end{aligned}
\right.
\tag{3-2}
\]
```

#### 显示公式 017，\tag{3-3}（正文第 551-564 行）

```latex
\[
\left\{
\begin{aligned}
&\tau_i=\begin{cases}\tau_{up},&|\omega_{cmd,i}|>|\omega_i|\\
\tau_{down},&\text{otherwise}\end{cases},\\
&\dot\omega_i=\frac{\omega_{cmd,i}-\omega_i}{\tau_i},\\
&T_{0,i}=C_T\omega_i^2,\\
&T_i=\eta_{f,i}\eta_{T,i}T_{0,i} .
\end{aligned}
\right.
\tag{3-3}
\]
```

#### 显示公式 018，\tag{3-4}（正文第 568-581 行）

```latex
\[
\left\{
\begin{aligned}
&\boldsymbol\tau_i=
\begin{bmatrix}r_{y,i}T_i\\-r_{x,i}T_i\\
\eta_{f,i}d_i\eta_{M,i}C_M\eta_{T,i}T_{0,i}\end{bmatrix},\\
&T=\sum_{i=1}^{4}T_i,\\
&\boldsymbol\tau=\sum_{i=1}^{4}\boldsymbol\tau_i .
\end{aligned}
\right.
\tag{3-4}
\]
```

#### 显示公式 019，\tag{3-5a}（正文第 585-590 行）

```latex
\[
\Delta T_{rotor}=2C_T\omega_h\Delta\omega.
\tag{3-5a}
\]
```

#### 显示公式 020，\tag{3-5b}（正文第 594-606 行）

```latex
\[
\left\{
\begin{aligned}
&\omega_{1,raw}= \omega_h+\Delta\omega_c-y-p+r,\\
&\omega_{2,raw}=-\omega_h-\Delta\omega_c-y+p+r,\\
&\omega_{3,raw}= \omega_h+\Delta\omega_c-y+p-r,\\
&\omega_{4,raw}=-\omega_h-\Delta\omega_c-y-p-r.
\end{aligned}
\right.
\tag{3-5b}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 四、统一控制器接口与 FormalRunner 执行边界

#### 显示公式 021，\tag{4-1}（正文第 656-669 行）

```latex
\[
(\mathbf p,\mathbf v,R,\boldsymbol\omega,\mathbf r)
\xrightarrow{\ \mathcal C_j\ }\boldsymbol\chi_j
\xrightarrow{\ \mathcal A_{b_j}\ }
\begin{cases}
(\boldsymbol\eta_c,T_c),&b_j=\mathrm{ATTITUDE\_THRUST},\\
(\boldsymbol\omega_c,T_c),&b_j=\mathrm{BODY\_RATE\_THRUST},\\
(\mathbf F_c,\boldsymbol\tau_c),&b_j=\mathrm{WRENCH},\\
\boldsymbol\omega_{cmd},&b_j=\mathrm{ROTOR\_COMMAND}.
\end{cases}
\tag{4-1}
\]
```

#### 显示公式 022，\tag{4-2}（正文第 683-694 行）

```latex
\[
\left\{
\begin{aligned}
&\mathcal D_{T_s}[s](t)=s((k-1)T_s),\\
&kT_s\le t<(k+1)T_s,\\
&\mathcal D_{T_s}[s](0)=0.
\end{aligned}
\right.
\tag{4-2}
\]
```

#### 显示公式 023，\tag{4-3}（正文第 698-711 行）

```latex
\[
\left\{
\begin{aligned}
&\tilde{\mathbf p}_r=\mathcal D_{T_s}[\mathbf p_r],\\
&\tilde{\mathbf v}_r=\mathcal D_{T_s}[\mathbf v_r],\\
&\tilde{\mathbf a}_r=\mathcal D_{T_s}[\mathbf a_r],\\
&\tilde{\mathbf p}=\mathcal D_{T_s}[\mathbf p],\\
&\tilde{\boldsymbol\eta}=\mathcal D_{T_s}[\boldsymbol\eta].
\end{aligned}
\right.
\tag{4-3}
\]
```

#### 显示公式 024，\tag{4-4}（正文第 715-720 行）

```latex
\[
\hat{\mathbf v}(s)=\frac{s}{T_v s+1}\tilde{\mathbf p}(s).
\tag{4-4}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 五、Official PID 工程基线

#### 显示公式 025，\tag{5-1}（正文第 731-736 行）

```latex
\[
\mathbf e_p=\mathbf p_r-\mathbf p
\tag{5-1}
\]
```

#### 显示公式 026，\tag{5-2}（正文第 740-745 行）

```latex
\[
\mathbf e_v=\dot{\mathbf e}_p=\mathbf v_r-\mathbf v
\tag{5-2}
\]
```

#### 显示公式 027，\tag{5-3}（正文第 749-759 行）

```latex
\[
\left\{
\begin{aligned}
&a_{c,x}=1.5e_x+\dot e_x\\
&a_{c,y}=1.5e_y+\dot e_y
\end{aligned}
\right.
\tag{5-3}
\]
```

#### 显示公式 028，\tag{5-4}（正文第 763-774 行）

```latex
\[
\left\{
\begin{aligned}
&\theta_r=\operatorname{sat}_{15/57.3}(0.1a_{c,x})\\
&\phi_r=\operatorname{sat}_{15/57.3}(0.1a_{c,y})\\
&t_r=8e_z+6\int e_z\,dt+4\dot e_z
\end{aligned}
\right.
\tag{5-4}
\]
```

#### 显示公式 029，\tag{5-5}（正文第 779-790 行）

```latex
\[
\left\{
\begin{aligned}
&e_\phi=\phi_r-\phi\\
&e_\theta=\theta_r-\theta\\
&e_\psi=\psi_r-\psi
\end{aligned}
\right.
\tag{5-5}
\]
```

#### 显示公式 030，\tag{5-6}（正文第 794-805 行）

```latex
\[
\left\{
\begin{aligned}
&u_\phi=14.142e_\phi+1.414\dot e_\phi,\\
&u_\theta=14.142e_\theta+1.414\dot e_\theta,\\
&u_\psi=5e_\psi,
\end{aligned}
\right.
\tag{5-6}
\]
```

#### 显示公式 031，\tag{5-7}（正文第 809-814 行）

```latex
\[
\bar a_\psi=\frac14\sum_{i=1}^{4}d_i a_i
\tag{5-7}
\]
```

#### 显示公式 032，\tag{5-8}（正文第 818-828 行）

```latex
\[
\left\{
\begin{aligned}
&a_i^{map}=\bigl(a_i-d_i\bar a_\psi\bigr)+d_i\gamma\bar a_\psi\\
&\omega_{cmd,i}=s_i\bigl(\omega_h+c\,a_i^{map}\bigr)
\end{aligned}
\right.
\tag{5-8}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > cascade_pid

#### 显示公式 033，\tag{6-1}（正文第 876-890 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf e_p=\mathbf p_r-\mathbf p,\\
&\mathbf e_v=\mathbf v_r-\mathbf v,\\
&\mathbf a_c=\mathbf a_r+K_{p,p}\mathbf e_p+K_{d,p}\mathbf e_v,\\
&\mathbf e_\eta=\boldsymbol\eta_r-\boldsymbol\eta,\\
&\mathbf e_\omega=\boldsymbol\omega_r-\boldsymbol\omega,\\
&\boldsymbol\omega_c=\boldsymbol\omega_r+K_{p,\eta}\mathbf e_\eta+K_{d,\eta}\mathbf e_\omega.
\end{aligned}
\right.
\tag{6-1}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > gain_scheduled_pid

#### 显示公式 034，\tag{6-2}（正文第 902-914 行）

```latex
\[
\left\{
\begin{aligned}
&\rho=\rho(\mathbf x,\mathbf r),\\
&z_e(t)=\int_0^t e(\tau)\,d\tau,\\
&K_j=K_j(\rho),\qquad j\in\{p,i,d\},\\
&u=K_p e+K_i z_e+K_d\dot e.
\end{aligned}
\right.
\tag{6-2}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > fuzzy_pid

#### 显示公式 035，\tag{6-3}（正文第 926-940 行）

```latex
\[
\left\{
\begin{aligned}
&\boldsymbol\xi=\begin{bmatrix}e&\dot e\end{bmatrix}^{T},\\
&\bar K_j(\boldsymbol\xi)=
\frac{\sum_{\ell=1}^{n_r}\mu_\ell(\boldsymbol\xi)K_{j,\ell}}
{\sum_{\ell=1}^{n_r}\mu_\ell(\boldsymbol\xi)},\qquad j\in\{p,i,d\},\\
&z_e(t)=\int_0^t e(\tau)\,d\tau,\\
&u=\bar K_p e+\bar K_i z_e+\bar K_d\dot e.
\end{aligned}
\right.
\tag{6-3}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > neural_pid

#### 显示公式 036，\tag{6-4}（正文第 952-964 行）

```latex
\[
\left\{
\begin{aligned}
&\boldsymbol\xi=\begin{bmatrix}e&\dot e&z_e\end{bmatrix}^{T},\\
&\mathbf h=\sigma(W_1\boldsymbol\xi+\mathbf b_1),\\
&\Delta u_{NN}=W_2\mathbf h+b_2,\\
&u=\operatorname{sat}_{[u_{\min},u_{\max}]}\!\left(u_{PID}+\Delta u_{NN}\right).
\end{aligned}
\right.
\tag{6-4}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > fopid

#### 显示公式 037，\tag{6-5}（正文第 976-989 行）

```latex
\[
\left\{
\begin{aligned}
&0<\lambda\leq 1,\qquad 0<\mu\leq 1,\\
&u_P=K_p e,\\
&u_I=K_iD^{-\lambda}e,\\
&u_D=K_dD^{\mu}e,\\
&u=u_P+u_I+u_D.
\end{aligned}
\right.
\tag{6-5}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > fixed_awff_pid

#### 显示公式 038，\tag{6-6}（正文第 1001-1013 行）

```latex
\[
\left\{
\begin{aligned}
&z_e(t)=\int_0^t e(\tau)\,d\tau,\\
&u_{PID}=K_p e+K_i z_e+K_d\dot e,\\
&u_{ff}=K_{ff}\dot r,\\
&u_{AWFF}=u_{PID}+u_{ff}.
\end{aligned}
\right.
\tag{6-6}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > fixed_awff_l1_residual

#### 显示公式 039，\tag{6-7}（正文第 1025-1037 行）

```latex
\[
\left\{
\begin{aligned}
&\dot{\hat{\mathbf x}}=A_m\hat{\mathbf x}+B_m\bigl(u_{AWFF}+\hat{\boldsymbol\sigma}\bigr),\\
&\tilde{\mathbf x}=\hat{\mathbf x}-\mathbf x,\\
&\Delta u_{L1}=C(s)\hat{\boldsymbol\sigma},\\
&u=\operatorname{sat}_{[u_{\min},u_{\max}]}\!\left(u_{AWFF}+\Delta u_{L1}\right).
\end{aligned}
\right.
\tag{6-7}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > fixed_awff_l1_indi

#### 显示公式 040，\tag{6-8}（正文第 1049-1060 行）

```latex
\[
\left\{
\begin{aligned}
&u_{nom}=u_{AWFF}+C(s)\hat{\boldsymbol\sigma},\\
&\Delta u_{INDI}=G^{\dagger}\!\left(\boldsymbol\nu-\widehat{\dot{\boldsymbol\omega}}\right),\\
&u=\operatorname{sat}_{[u_{\min},u_{\max}]}\!\left(u_{nom}+\Delta u_{INDI}\right).
\end{aligned}
\right.
\tag{6-8}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > pid_awff_linear_eso

#### 显示公式 041，\tag{6-9}（正文第 1072-1086 行）

```latex
\[
\left\{
\begin{aligned}
&u_0=u_{AWFF},\\
&\epsilon=e-z_1,\\
&\dot z_1=z_2+3\omega_o\epsilon,\\
&\dot z_2=z_3+b_0u_0+3\omega_o^2\epsilon,\\
&\dot z_3=\omega_o^3\epsilon,\\
&u=\operatorname{sat}_{[u_{\min},u_{\max}]}\!\left(u_0-\frac{z_3}{b_0}\right).
\end{aligned}
\right.
\tag{6-9}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > lqr_baseline

#### 显示公式 042，\tag{6-10}（正文第 1102-1117 行）

```latex
\[
\left\{
\begin{aligned}
&J_{\mathrm{LQR}}=\int_{0}^{\infty}
\left(\tilde{\mathbf x}^{T}Q\tilde{\mathbf x}
+\tilde{\mathbf u}^{T}R\tilde{\mathbf u}\right)dt,\\
&A^{T}P+PA-PBR^{-1}B^{T}P+Q=\mathbf 0,\\
&K_{\mathrm{LQR}}=R^{-1}B^{T}P,\\
&\tilde{\mathbf u}=-K_{\mathrm{LQR}}\tilde{\mathbf x},\\
&\mathbf u_c=\mathbf u_{\mathrm{trim}}+\tilde{\mathbf u}+N_r\mathbf r.
\end{aligned}
\right.
\tag{6-10}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > lqi_baseline

#### 显示公式 043，\tag{6-11}（正文第 1129-1144 行）

```latex
\[
\left\{
\begin{aligned}
&\bar{\mathbf x}_k=\begin{bmatrix}\tilde{\mathbf x}_k^{T}&\boldsymbol\zeta_k^{T}\end{bmatrix}^{T},\\
&\boldsymbol\zeta_{k+1}=\operatorname{sat}_{[-\boldsymbol\zeta_{\max},\boldsymbol\zeta_{\max}]}
\!\left(\boldsymbol\zeta_k+T_s(\mathbf r_k-\mathbf y_k)\right),\\
&J_{\mathrm{LQI}}=\sum_{k=0}^{\infty}
\left(\bar{\mathbf x}_k^{T}\bar Q\bar{\mathbf x}_k+\tilde{\mathbf u}_k^{T}R\tilde{\mathbf u}_k\right),\\
&\tilde{\mathbf u}_k=-K_x\tilde{\mathbf x}_k-K_I\boldsymbol\zeta_k,\\
&\mathbf u_{c,k}=\mathbf u_{\mathrm{trim}}+\tilde{\mathbf u}_k+N_r\mathbf r_k.
\end{aligned}
\right.
\tag{6-11}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > lqg

#### 显示公式 044，\tag{6-12}（正文第 1156-1172 行）

```latex
\[
\left\{
\begin{aligned}
&\widehat{\mathbf p}_{k+1|k}=\widehat{\mathbf p}_k+T_s\widehat{\mathbf v}_k,\\
&\widehat{\mathbf p}_{k+1}=\widehat{\mathbf p}_{k+1|k}
+L_p\left(\mathbf p_k-\widehat{\mathbf p}_{k+1|k}\right),\\
&\mathbf a_{c,k}=\mathbf a_{r,k}+K_p\left(\mathbf p_{r,k}-\widehat{\mathbf p}_k\right)
+K_v\left(\mathbf v_{r,k}-\widehat{\mathbf v}_k\right)+g\mathbf e_3,\\
&\widehat{\mathbf v}_{k+1|k}=\widehat{\mathbf v}_k+T_s\left(\mathbf a_{c,k}-g\mathbf e_3\right),\\
&\widehat{\mathbf v}_{k+1}=\widehat{\mathbf v}_{k+1|k}
+L_v\left(\mathbf v_k-\widehat{\mathbf v}_{k+1|k}\right).
\end{aligned}
\right.
\tag{6-12}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > h2_state_feedback

#### 显示公式 045，\tag{6-13}（正文第 1184-1197 行）

```latex
\[
\left\{
\begin{aligned}
&A_{cl}=A+BK_{H_2},\\
&A_{cl}^{T}P+PA_{cl}+C_z^{T}C_z=\mathbf 0,\\
&J_{H_2}=\left\|T_{w\rightarrow z}(K_{H_2})\right\|_{2}^{2},\\
&K_{H_2}^{\star}=\arg\min_K J_{H_2},\\
&\tilde{\mathbf u}=K_{H_2}^{\star}\tilde{\mathbf x}.
\end{aligned}
\right.
\tag{6-13}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > hinf_hover_wrench

#### 显示公式 046，\tag{6-14}（正文第 1209-1222 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf w_c=\begin{bmatrix}F_z&\tau_x&\tau_y&\tau_z\end{bmatrix}^{T},\\
&A_{cl}=A+BK_{\infty},\\
&\gamma^{\star}=\min_K\left\|T_{w\rightarrow z}(K)\right\|_{\infty},\\
&\left\|T_{w\rightarrow z}(K_{\infty}^{\star})\right\|_{\infty}<\gamma,\\
&\mathbf w_c=\operatorname{sat}_{\mathcal W}\!\left(K_{\infty}^{\star}\tilde{\mathbf x}\right).
\end{aligned}
\right.
\tag{6-14}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > pole_placement_luenberger

#### 显示公式 047，\tag{6-15}（正文第 1234-1248 行）

```latex
\[
\left\{
\begin{aligned}
&\operatorname{eig}(A-BK)=\mathcal P_c,\\
&\dot{\widehat{\mathbf x}}=A\widehat{\mathbf x}+B\tilde{\mathbf u}
+L\left(\mathbf y-C\widehat{\mathbf x}\right),\\
&\operatorname{eig}(A-LC)=\mathcal P_o,\\
&\tilde{\mathbf u}=-K\widehat{\mathbf x},\\
&\mathbf u_c=\mathbf u_{\mathrm{trim}}+\tilde{\mathbf u}+N_r\mathbf r.
\end{aligned}
\right.
\tag{6-15}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > backstepping_baseline

#### 显示公式 048，\tag{6-16}（正文第 1264-1277 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf z_1=\mathbf p-\mathbf p_r,\\
&\boldsymbol\alpha_1=\dot{\mathbf p}_r-K_1\mathbf z_1,\\
&\mathbf z_2=\mathbf v-\boldsymbol\alpha_1,\\
&\mathbf u_{bs}=\dot{\boldsymbol\alpha}_1-K_2\mathbf z_2-\mathbf z_1,\\
&\mathbf a_c=\operatorname{sat}_{\mathcal A}(\mathbf u_{bs}).
\end{aligned}
\right.
\tag{6-16}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > adaptive_backstepping

#### 显示公式 049，\tag{6-17}（正文第 1289-1301 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf u=\mathbf u_{bs}-\hat{\mathbf d},\\
&\tilde{\mathbf d}=\mathbf d-\hat{\mathbf d},\\
&\dot{\hat{\mathbf d}}=-\Gamma\boldsymbol\Phi^{T}\mathbf z_2,\\
&\mathbf a_c=\operatorname{sat}_{\mathcal A}(\mathbf u).
\end{aligned}
\right.
\tag{6-17}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > feedback_linearization

#### 显示公式 050，\tag{6-18}（正文第 1313-1326 行）

```latex
\[
\left\{
\begin{aligned}
&\tilde{\mathbf e}_p=\mathbf p-\mathbf p_r,\\
&\tilde{\mathbf e}_v=\mathbf v-\dot{\mathbf p}_r,\\
&\ddot{\mathbf p}=\mathbf f(\mathbf x)+G(\mathbf x)\mathbf u,\\
&\boldsymbol\nu=\ddot{\mathbf p}_r-K_d\tilde{\mathbf e}_v-K_p\tilde{\mathbf e}_p,\\
&\mathbf u=G(\mathbf x)^{\dagger}\!\left[\boldsymbol\nu-\mathbf f(\mathbf x)\right].
\end{aligned}
\right.
\tag{6-18}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > passivity_based_control

#### 显示公式 051，\tag{6-19}（正文第 1338-1350 行）

```latex
\[
\left\{
\begin{aligned}
&V(\mathbf e_p,\mathbf e_v)=\frac{1}{2}\mathbf e_v^{T}M\mathbf e_v+U(\mathbf e_p),\\
&\nabla_{\mathbf e_p}U=K_p\mathbf e_p,\\
&\mathbf u=\mathbf u_{ff}-K_d\mathbf e_v-\nabla_{\mathbf e_p}U,\\
&\dot V=-\mathbf e_v^{T}K_d\mathbf e_v\leq 0.
\end{aligned}
\right.
\tag{6-19}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > mrac

#### 显示公式 052，\tag{6-20}（正文第 1362-1375 行）

```latex
\[
\left\{
\begin{aligned}
&\dot{\mathbf x}_m=A_m\mathbf x_m+B_m\mathbf r,\\
&\mathbf e_m=\mathbf x-\mathbf x_m,\\
&\mathbf u=\hat{\Theta}^{T}\boldsymbol\phi(\mathbf x,\mathbf r),\\
&A_m^{T}P+PA_m=-Q,\\
&\dot{\hat{\Theta}}=-\Gamma\boldsymbol\phi\,\mathbf e_m^{T}PB.
\end{aligned}
\right.
\tag{6-20}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > ndi

#### 显示公式 053，\tag{6-21}（正文第 1387-1400 行）

```latex
\[
\left\{
\begin{aligned}
&\dot{\mathbf x}=\mathbf f(\mathbf x)+B(\mathbf x)\mathbf u,\\
&\tilde{\mathbf e}=\mathbf x-\mathbf x_r,\\
&\boldsymbol\nu=\dot{\mathbf x}_r-K\tilde{\mathbf e},\\
&\mathbf u=B(\mathbf x)^{\dagger}\!\left[\boldsymbol\nu-\mathbf f(\mathbf x)\right],\\
&\dot{\tilde{\mathbf e}}=-K\tilde{\mathbf e}.
\end{aligned}
\right.
\tag{6-21}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > integral_smc

#### 显示公式 054，\tag{6-22}（正文第 1421-1434 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf z_{I,k+1}=\operatorname{sat}_{[-\mathbf z_{I,\max},\mathbf z_{I,\max}]}
\!\left(\mathbf z_{I,k}+T_s\mathbf e_{p,k}\right),\\
&\mathbf s_k=\mathbf e_{v,k}+\Lambda_p\mathbf e_{p,k}+\Lambda_I\mathbf z_{I,k},\\
&\mathbf a_{c,k}=\mathbf a_{r,k}+K_v\mathbf e_{v,k}+K_s\mathbf s_k
+K_r\operatorname{sat}_{[-\mathbf 1,\mathbf 1]}(\Phi\mathbf s_k)+g\mathbf e_3.
\end{aligned}
\right.
\tag{6-22}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > terminal_smc

#### 显示公式 055，\tag{6-23}（正文第 1446-1458 行）

```latex
\[
\left\{
\begin{aligned}
&0<\alpha=\frac{p}{q}<1,\\
&\mathbf s=\mathbf e_v+\Lambda\operatorname{sgn}(\mathbf e_p)\odot|\mathbf e_p|^{\alpha},\\
&\mathbf a_c=\mathbf a_r+K_v\mathbf e_v+K_s\mathbf s
+K_r\operatorname{sat}_{[-\mathbf 1,\mathbf 1]}(\Phi\mathbf s)+g\mathbf e_3.
\end{aligned}
\right.
\tag{6-23}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > nonsingular_terminal_smc

#### 显示公式 056，\tag{6-24}（正文第 1470-1483 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf s=\mathbf e_v+\Lambda_p\mathbf e_p
+\Lambda_t\operatorname{sgn}(\mathbf e_p)\odot|\mathbf e_p|^{\beta},\\
&\beta>1,\\
&\mathbf a_c=\mathbf a_r+K_v\mathbf e_v+K_s\mathbf s
+K_r\operatorname{sat}_{[-\mathbf 1,\mathbf 1]}(\Phi\mathbf s)+g\mathbf e_3.
\end{aligned}
\right.
\tag{6-24}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > adaptive_smc

#### 显示公式 057，\tag{6-25}（正文第 1495-1508 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf s_k=\mathbf e_{v,k}+\Lambda\mathbf e_{p,k},\\
&\hat{\mathbf K}_{k+1}=\operatorname{sat}_{[\mathbf K_{\min},\mathbf K_{\max}]}
\!\left(\hat{\mathbf K}_k+\Gamma\bigl(|\mathbf s_k|-\boldsymbol\delta\bigr)\right),\\
&\mathbf a_{c,k}=\mathbf a_{r,k}+K_v\mathbf e_{v,k}+K_s\mathbf s_k
+\hat{\mathbf K}_{k}\odot\operatorname{sat}_{[-\mathbf 1,\mathbf 1]}(\Phi\mathbf s_k)+g\mathbf e_3.
\end{aligned}
\right.
\tag{6-25}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > fuzzy_smc

#### 显示公式 058，\tag{6-26}（正文第 1520-1532 行）

```latex
\[
\left\{
\begin{aligned}
&\boldsymbol\chi=\operatorname{sat}_{[\mathbf 0,\mathbf 1]}\!\left(\Psi|\mathbf s|\right),\\
&\mathbf K_f(\mathbf s)=\mathbf K_0+\Delta\mathbf K\odot\boldsymbol\chi\odot(2\mathbf 1-\boldsymbol\chi),\\
&\mathbf a_c=\mathbf a_r+K_v\mathbf e_v+K_s\mathbf s
+\mathbf K_f(\mathbf s)\odot\operatorname{sat}_{[-\mathbf 1,\mathbf 1]}(\Phi\mathbf s)+g\mathbf e_3.
\end{aligned}
\right.
\tag{6-26}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > super_twisting_smc

#### 显示公式 059，\tag{6-27}（正文第 1544-1556 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf s=\mathbf e_v+\Lambda\mathbf e_p,\\
&\mathbf u_{st}=-K_1|\mathbf s|^{1/2}\odot\operatorname{sgn}(\mathbf s)+\mathbf z,\\
&\dot{\mathbf z}=-K_2\operatorname{sgn}(\mathbf s),\\
&\mathbf a_c=\operatorname{sat}_{\mathcal A}\!\left(\mathbf a_r+\mathbf u_{st}+g\mathbf e_3\right).
\end{aligned}
\right.
\tag{6-27}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > smc_boundary_layer

#### 显示公式 060，\tag{6-28}（正文第 1568-1579 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf s=\Lambda\mathbf e_p+\mathbf e_v,\\
&\mathbf b=\operatorname{sat}_{[\mathbf b_{\min},\mathbf b_{\max}]}(\mathbf s),\\
&\mathbf a_c=\operatorname{sat}_{\mathcal A}\!\left(\mathbf a_r+K_{sw}\mathbf b\right).
\end{aligned}
\right.
\tag{6-28}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > linear_mpc

#### 显示公式 061，\tag{6-29}（正文第 1595-1612 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf x_{i+1|k}=A_d\mathbf x_{i|k}+B_d\mathbf u_{i|k},\\
&J_k(\mathbf U_k)=\sum_{i=0}^{N-1}\left[
\left(\mathbf x_{i|k}-\mathbf r_{i|k}\right)^{T}Q
\left(\mathbf x_{i|k}-\mathbf r_{i|k}\right)
+\mathbf u_{i|k}^{T}R\mathbf u_{i|k}\right],\\
&\mathbf U_k^{\star}=\arg\min_{\mathbf U_k}J_k(\mathbf U_k),\\
&\mathbf x_{i|k}\in\mathcal X,\\
&\mathbf u_{i|k}\in\mathcal U,\\
&\mathbf u_k=\mathbf u_{0|k}^{\star}.
\end{aligned}
\right.
\tag{6-29}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > robust_mpc

#### 显示公式 062，\tag{6-30}（正文第 1624-1637 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf x_{i+1|k}=A_d\mathbf x_{i|k}+B_d\mathbf u_{i|k}+E_d\mathbf w_{i|k},\\
&J_k^{\mathrm{rob}}(\mathbf U_k)=\max_{\mathbf w_{i|k}\in\mathcal W}J_k(\mathbf U_k,\mathbf w),\\
&\mathbf U_k^{\star}=\arg\min_{\mathbf U_k}J_k^{\mathrm{rob}}(\mathbf U_k),\\
&\mathbf x_{i|k}\in\mathcal X_{\mathrm{rob}},\\
&\mathbf u_k=\mathbf u_{0|k}^{\star}.
\end{aligned}
\right.
\tag{6-30}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > adaptive_mpc

#### 显示公式 063，\tag{6-31}（正文第 1649-1662 行）

```latex
\[
\left\{
\begin{aligned}
&\hat{\boldsymbol\theta}_{k+1}=\mathcal I\!\left(\hat{\boldsymbol\theta}_{k},\mathbf x_k,\mathbf u_{k-1}\right),\\
&A_{d,k}=A_d\!\left(\hat{\boldsymbol\theta}_{k}\right),\\
&B_{d,k}=B_d\!\left(\hat{\boldsymbol\theta}_{k}\right),\\
&\mathbf U_k^{\star}=\arg\min_{\mathbf U_k}J_k\!\left(A_{d,k},B_{d,k},\mathbf U_k\right),\\
&\mathbf u_k=\mathbf u_{0|k}^{\star}.
\end{aligned}
\right.
\tag{6-31}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > tube_mpc

#### 显示公式 064，\tag{6-32}（正文第 1674-1688 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf x_k=\mathbf z_k+\mathbf e_k,\\
&\mathbf z_{k+1}=A_d\mathbf z_k+B_d\mathbf v_k,\\
&\mathbf u_k=\mathbf v_k+K_e\mathbf e_k,\\
&\mathbf e_k\in\mathcal Z,\\
&\mathbf z_k\in\mathcal X\ominus\mathcal Z,\\
&\mathbf v_k\in\mathcal U\ominus K_e\mathcal Z.
\end{aligned}
\right.
\tag{6-32}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > explicit_gain_scheduled_mpc

#### 显示公式 065，\tag{6-33}（正文第 1700-1712 行）

```latex
\[
\left\{
\begin{aligned}
&i_k=\mathcal I\!\left(\mathbf x_k,\rho_k\right),\\
&\left(\mathbf x_k,\rho_k\right)\in\mathcal R_{i_k},\\
&\mathbf u_k^{\mathrm{raw}}=K_{i_k}(\rho_k)\mathbf x_k+c_{i_k}(\rho_k),\\
&\mathbf u_k=\operatorname{sat}_{\mathcal U}\!\left(\mathbf u_k^{\mathrm{raw}}\right).
\end{aligned}
\right.
\tag{6-33}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > ilqr

#### 显示公式 066，\tag{6-34}（正文第 1724-1736 行）

```latex
\[
\left\{
\begin{aligned}
&\delta\mathbf x_{k+1}=A_k\delta\mathbf x_k+B_k\delta\mathbf u_k,\\
&\delta\mathbf u_k=\mathbf k_k+K_k\delta\mathbf x_k,\\
&\mathbf u_k=\bar{\mathbf u}_k+\delta\mathbf u_k,\\
&\bar{\mathbf u}_k^{+}=\bar{\mathbf u}_k+\alpha\mathbf k_k.
\end{aligned}
\right.
\tag{6-34}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > mppi

#### 显示公式 067，\tag{6-35}（正文第 1748-1761 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf u_{m,t}=\bar{\mathbf u}_t+\boldsymbol\epsilon_{m,t},\\
&S_m=\sum_{i=0}^{N-1}\ell\!\left(\mathbf x_{m,i},\mathbf u_{m,i}\right),\\
&w_m=\frac{\exp\!\left[-(S_m-S_{\min})/\lambda\right]}
{\sum_j\exp\!\left[-(S_j-S_{\min})/\lambda\right]},\\
&\mathbf u_t=\bar{\mathbf u}_t+\sum_m w_m\boldsymbol\epsilon_{m,t}.
\end{aligned}
\right.
\tag{6-35}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > nmpc_outer

#### 显示公式 068，\tag{6-36}（正文第 1773-1787 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf x_{i+1|k}=f\!\left(\mathbf x_{i|k},\mathbf u_{i|k}\right),\\
&\mathbf U_k^{\star}=\arg\min_{\mathbf U_k}
\sum_{i=0}^{N-1}\ell\!\left(\mathbf x_{i|k},\mathbf u_{i|k}\right),\\
&\mathbf x_{i|k}\in\mathcal X,\\
&\mathbf u_{i|k}\in\mathcal U,\\
&\mathbf u_k=\mathbf u_{0|k}^{\star}.
\end{aligned}
\right.
\tag{6-36}
\]
```

#### 显示公式 069，\tag{6-36a}（正文第 1791-1804 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf h_k=K_p^{h}\mathbf e_{p,k}+K_v^{h}\mathbf e_{v,k},\\
&\mathbf u_k^{\mathrm{raw}}=K_q\mathbf h_k,\\
&\Delta\mathbf u_k=\operatorname{sat}_{[\Delta\mathbf u_{\min},\Delta\mathbf u_{\max}]}
\!\left(\mathbf u_k^{\mathrm{raw}}-\mathbf u_{k-1}\right),\\
&\mathbf a_{c,k}=\operatorname{sat}_{[-\mathbf a_{\max},\mathbf a_{\max}]}\!\left(\Delta\mathbf u_k\right).
\end{aligned}
\right.
\tag{6-36a}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > fixed_linear_mpc_l1_indi

#### 显示公式 070，\tag{6-37}（正文第 1816-1829 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf u_{nom}=\mathbf u_{\mathrm{LMPC}},\\
&\Delta\mathbf u_{L1}=C(s)\hat{\boldsymbol\sigma},\\
&\Delta\mathbf u_{INDI}=G^{\dagger}\!\left(\boldsymbol\nu-\widehat{\dot{\boldsymbol\omega}}\right),\\
&\mathbf u=\operatorname{sat}_{\mathcal U}\!\left(
\mathbf u_{nom}+\Delta\mathbf u_{L1}+\Delta\mathbf u_{INDI}\right).
\end{aligned}
\right.
\tag{6-37}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > fixed_qp_nmpc_l1_indi_cbf

#### 显示公式 071，\tag{6-38}（正文第 1841-1856 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf u_{QP}^{\star}=\arg\min_{\mathbf u}
\left\|\mathbf u-\mathbf u_{NMPC}\right\|_{H}^{2},\\
&\dot h(\mathbf x,\mathbf u)+\alpha h(\mathbf x)\geq 0,\\
&\Delta\mathbf u_{L1}=C(s)\hat{\boldsymbol\sigma},\\
&\Delta\mathbf u_{INDI}=G^{\dagger}\!\left(\boldsymbol\nu-\widehat{\dot{\boldsymbol\omega}}\right),\\
&\mathbf u=\operatorname{sat}_{\mathcal U}\!\left(
\mathbf u_{QP}^{\star}+\Delta\mathbf u_{L1}+\Delta\mathbf u_{INDI}\right).
\end{aligned}
\right.
\tag{6-38}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > se3_basic

#### 显示公式 072，\tag{6-39}（正文第 1872-1888 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf e_R=\frac{1}{2}\!\left(R_r^{T}R-R^{T}R_r\right)^{\vee},\\
&\mathbf e_\Omega=\boldsymbol\Omega-R^{T}R_r\boldsymbol\Omega_r,\\
&\mathbf F_c=-K_p\tilde{\mathbf e}_p-K_v\tilde{\mathbf e}_v
+m\mathbf a_r+mg\mathbf e_3,\\
&\mathbf M_c=-K_R\mathbf e_R-K_\Omega\mathbf e_\Omega
+\boldsymbol\Omega\times J\boldsymbol\Omega
-J\!\left(\widehat{\boldsymbol\Omega}R^{T}R_r\boldsymbol\Omega_r
-R^{T}R_r\dot{\boldsymbol\Omega}_r\right).
\end{aligned}
\right.
\tag{6-39}
\]
```

#### 显示公式 073，\tag{6-39a}（正文第 1892-1906 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf a_c=\mathbf a_r+1.5\mathbf e_p+1.5\mathbf e_v,\\
&\phi_d=\operatorname{sat}_{[-\phi_{\max},\phi_{\max}]}
\!\left(c_\phi a_{c,y}\right),\\
&\theta_d=\operatorname{sat}_{[-\theta_{\max},\theta_{\max}]}
\!\left(c_\theta a_{c,x}\right),\\
&T_n=\operatorname{sat}_{[0,1]}\!\left(c_T(a_{c,z}+g)\right).
\end{aligned}
\right.
\tag{6-39a}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > dfbc_basic

#### 显示公式 074，\tag{6-40}（正文第 1918-1936 行）

```latex
\[
\left\{
\begin{aligned}
&q_k=q_0,\\
&\delta d_k=k_d q_{k-1},\\
&\mathbf a_{c,k}=\operatorname{sat}_{[-a_{\max},a_{\max}]}
\!\left(\mathbf a_{r,k}+K_p\mathbf e_{p,k}+K_v\mathbf e_{v,k}
+\delta d_k\mathbf 1\right),\\
&\phi_{d,k}=\operatorname{sat}_{[-\phi_{\max},\phi_{\max}]}
\!\left(c_\phi a_{c,y,k}\right),\\
&\theta_{d,k}=\operatorname{sat}_{[-\theta_{\max},\theta_{\max}]}
\!\left(c_\theta a_{c,x,k}\right),\\
&T_{n,k}=\operatorname{sat}_{[0,1]}\!\left(c_T(a_{c,z,k}+g)\right).
\end{aligned}
\right.
\tag{6-40}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > dfbc_smooth_robust_attitude

#### 显示公式 075，\tag{6-41}（正文第 1948-1967 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf s_k=K_p\mathbf e_{p,k}+K_v\mathbf e_{v,k},\\
&\hat{\mathbf d}_{k+1}=\operatorname{sat}_{[-\bar{\mathbf d},\bar{\mathbf d}]}
\!\left(\hat{\mathbf d}_k+L_d(\mathbf s_k-\hat{\mathbf d}_k)\right),\\
&\mathbf a_{c,k}=\operatorname{sat}_{[-\mathbf a_{\max},\mathbf a_{\max}]}
\!\left(\mathbf a_{r,k}+\mathbf s_k
+K_g\odot\tanh(\Psi\mathbf s_k)-\hat{\mathbf d}_k\right),\\
&\phi_{d,k}=\operatorname{sat}_{[-\phi_{\max},\phi_{\max}]}
\!\left(c_\phi a_{c,y,k}\right),\\
&\theta_{d,k}=\operatorname{sat}_{[-\theta_{\max},\theta_{\max}]}
\!\left(c_\theta a_{c,x,k}\right),\\
&T_{n,k}=\operatorname{sat}_{[0,1]}\!\left(c_T(a_{c,z,k}+g)\right).
\end{aligned}
\right.
\tag{6-41}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > dfbc_smooth_robust_bodyrate

#### 显示公式 076，\tag{6-42}（正文第 1979-1993 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf s_k=K_p\mathbf e_{p,k}+K_v\mathbf e_{v,k},\\
&\hat{\mathbf d}_{k+1}=\operatorname{sat}_{[-\bar{\mathbf d},\bar{\mathbf d}]}
\!\left(\hat{\mathbf d}_k+L_d(\mathbf s_k-\hat{\mathbf d}_k)\right),\\
&\mathbf a_{c,k}=\operatorname{sat}_{[-\mathbf a_{\max},\mathbf a_{\max}]}
\!\left(\mathbf a_{r,k}+\mathbf s_k
+K_g\odot\tanh(\Psi\mathbf s_k)-\hat{\mathbf d}_k\right),
\end{aligned}
\right.
\tag{6-42}
\]
```

#### 显示公式 077，\tag{6-43}（正文第 1997-2009 行）

```latex
\[
\begin{aligned}
&\omega_{r,x,k}=\operatorname{sat}_{[-\omega_{x,\max},\omega_{x,\max}]}
\!\left(c_{\omega x}a_{c,x,k}\right),\\
&\omega_{r,y,k}=\operatorname{sat}_{[-\omega_{y,\max},\omega_{y,\max}]}
\!\left(c_{\omega y}a_{c,y,k}\right),\\
&\omega_{r,z,k}=0,\\
&T_{n,k}=\operatorname{sat}_{[0,1]}\!\left(c_T(a_{c,z,k}+g)\right).
\end{aligned}
\tag{6-43}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > dfbc_high_order_attitude

#### 显示公式 078，\tag{6-44}（正文第 2021-2033 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf s_k=K_p\mathbf e_{p,k}+K_v\mathbf e_{v,k},\\
&\dot{\mathbf s}^{\Delta}_k=\frac{\mathbf s_k-\mathbf s_{k-1}}{T_s},\\
&\mathbf a_{c,k}=\operatorname{sat}_{[-\mathbf a_{\max},\mathbf a_{\max}]}
\!\left(\mathbf a_{r,k}+\mathbf s_k+K_h\odot\dot{\mathbf s}^{\Delta}_k\right),
\end{aligned}
\right.
\tag{6-44}
\]
```

#### 显示公式 079，\tag{6-45}（正文第 2037-2048 行）

```latex
\[
\begin{aligned}
&\phi_{d,k}=\operatorname{sat}_{[-\phi_{\max},\phi_{\max}]}
\!\left(c_\phi a_{c,y,k}\right),\\
&\theta_{d,k}=\operatorname{sat}_{[-\theta_{\max},\theta_{\max}]}
\!\left(c_\theta a_{c,x,k}\right),\\
&T_{n,k}=\operatorname{sat}_{[0,1]}\!\left(c_T(a_{c,z,k}+g)\right).
\end{aligned}
\tag{6-45}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > dfbc_high_order_bodyrate

#### 显示公式 080，\tag{6-46}（正文第 2060-2072 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf s_k=K_p\mathbf e_{p,k}+K_v\mathbf e_{v,k},\\
&\dot{\mathbf s}^{\Delta}_k=\frac{\mathbf s_k-\mathbf s_{k-1}}{T_s},\\
&\mathbf a_{c,k}=\operatorname{sat}_{[-\mathbf a_{\max},\mathbf a_{\max}]}
\!\left(\mathbf a_{r,k}+\mathbf s_k+K_h\odot\dot{\mathbf s}^{\Delta}_k\right),
\end{aligned}
\right.
\tag{6-46}
\]
```

#### 显示公式 081，\tag{6-47}（正文第 2076-2088 行）

```latex
\[
\begin{aligned}
&\omega_{r,x,k}=\operatorname{sat}_{[-\omega_{x,\max},\omega_{x,\max}]}
\!\left(c_{\omega x}a_{c,x,k}\right),\\
&\omega_{r,y,k}=\operatorname{sat}_{[-\omega_{y,\max},\omega_{y,\max}]}
\!\left(c_{\omega y}a_{c,y,k}\right),\\
&\omega_{r,z,k}=0,\\
&T_{n,k}=\operatorname{sat}_{[0,1]}\!\left(c_T(a_{c,z,k}+g)\right).
\end{aligned}
\tag{6-47}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.8 学习控制的 2 条公式 > rl_gain_scheduler

#### 显示公式 082，\tag{6-48}（正文第 2108-2121 行）

```latex
\[
\left\{
\begin{aligned}
&\boldsymbol\xi_k=\left[\mathbf e_{p,k}^{T},\mathbf e_{v,k}^{T},
\mathbf a_{r,k}^{T},\psi_{r,k}\right]^{T},\\
&\mathbf K^{\mathrm{raw}}_k=\pi_\theta(\boldsymbol\xi_k),\\
&\mathbf K_k=\operatorname{sat}_{[\mathbf K_{\min},\mathbf K_{\max}]}
\!\left(\mathbf K^{\mathrm{raw}}_k\right),
\end{aligned}
\right.
\tag{6-48}
\]
```

#### 显示公式 083，\tag{6-49}（正文第 2125-2137 行）

```latex
\[
\begin{aligned}
&\mathbf z_{I,k+1}=\operatorname{sat}_{[-\mathbf z_{I,\max},\mathbf z_{I,\max}]}
\!\left(\mathbf z_{I,k}+T_s\mathbf e_{p,k}\right),\\
&\mathbf u_{\mathrm{PID},k}=\mathbf K_{p,k}\odot\mathbf e_{p,k}
+\mathbf K_{i,k}\odot\mathbf z_{I,k}
+\mathbf K_{d,k}\odot\mathbf e_{v,k},\\
&\mathbf u_k=\operatorname{sat}_{\mathcal U}\!\left(\mathbf u_{\mathrm{PID},k}\right).
\end{aligned}
\tag{6-49}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.8 学习控制的 2 条公式 > trained_neural_residual

#### 显示公式 084，\tag{6-50}（正文第 2149-2166 行）

```latex
\[
\left\{
\begin{aligned}
&\boldsymbol\xi_k=\left[\mathbf e_{p,k}^{T},\mathbf e_{v,k}^{T},
\mathbf a_{r,k}^{T},\psi_{r,k}\right]^{T},\\
&\Delta\mathbf u^{\mathrm{raw}}_k=f_\theta(\boldsymbol\xi_k),\\
&\Delta\mathbf u_k=\mathbf g\odot\operatorname{sat}_{[-\Delta\mathbf u_{\max},\Delta\mathbf u_{\max}]}
\!\left(\Delta\mathbf u^{\mathrm{raw}}_k\right),\\
&\mathbf u_{c,k}=\operatorname{sat}_{\mathcal U}
\!\left(\mathbf u_{\mathrm{nom},k}+\Delta\mathbf u_k\right),\\
&\mathbf u_k=(1-b_{\mathrm{fb},k})\mathbf u_{c,k}
+b_{\mathrm{fb},k}\mathbf u_{\mathrm{nom},k},\qquad b_{\mathrm{fb},k}\in\{0,1\}.
\end{aligned}
\right.
\tag{6-50}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 八、px4ctrl 图形化设计与 MWORKS 全机验证

#### 显示公式 085，\tag{8-1}（正文第 4095-4105 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf e_p=\mathbf p_r-\mathbf p\\
&\mathbf e_v=\dot{\mathbf e}_p=\mathbf v_r-\mathbf v
\end{aligned}
\right.
\tag{8-1}
\]
```

#### 显示公式 086，\tag{8-2}（正文第 4109-4114 行）

```latex
\[
\mathbf a_{fb}=K_p\mathbf e_p+K_v\mathbf e_v
\tag{8-2}
\]
```

#### 显示公式 087，\tag{8-3}（正文第 4118-4123 行）

```latex
\[
\mathbf a_c=\mathbf a_r+\mathbf a_{fb}
\tag{8-3}
\]
```

#### 显示公式 088，\tag{8-4}（正文第 4127-4132 行）

```latex
\[
\mathbf a_d=\mathbf a_c+\begin{bmatrix}0\\0\\g\end{bmatrix}
\tag{8-4}
\]
```

#### 显示公式 089，\tag{8-5a}（正文第 4137-4148 行）

```latex
\[
\begin{bmatrix}a_{d,x}\\a_{d,y}\end{bmatrix}
\approx
g\begin{bmatrix}
\sin\psi & \cos\psi\\
-\cos\psi & \sin\psi
\end{bmatrix}
\begin{bmatrix}\phi_c\\\theta_c\end{bmatrix}.
\tag{8-5a}
\]
```

#### 显示公式 090，\tag{8-5b}（正文第 4152-4164 行）

```latex
\[
\begin{bmatrix}\phi_c\\\theta_c\end{bmatrix}
=
\frac{1}{g}
\begin{bmatrix}
\sin\psi & -\cos\psi\\
\cos\psi & \sin\psi
\end{bmatrix}
\begin{bmatrix}a_{d,x}\\a_{d,y}\end{bmatrix}.
\tag{8-5b}
\]
```

#### 显示公式 091，\tag{8-5}（正文第 4169-4180 行）

```latex
\[
\left\{
\begin{aligned}
&\phi_c=\frac{a_{d,x}\sin\psi-a_{d,y}\cos\psi}{g}\\
&\theta_c=\frac{a_{d,x}\cos\psi+a_{d,y}\sin\psi}{g}\\
&\psi_c=\psi_r
\end{aligned}
\right.
\tag{8-5}
\]
```

#### 显示公式 092，\tag{8-6}（正文第 4185-4190 行）

```latex
\[
T_c=m a_{d,z}
\tag{8-6}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十、三机编队 Figure8 与 ECBF 安全参考调节 > 10.2 三机 ECBF 安全参考调节

#### 显示公式 093，\tag{10-1}（正文第 4442-4456 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf r_{ij}=\mathbf p_i-\mathbf p_j,\\
&\mathbf v_{ij}=\mathbf v_i-\mathbf v_j,\\
&a_{ij,req}=-\lVert\mathbf v_{ij}\rVert_2^2
-2\lambda\mathbf r_{ij}^T\mathbf v_{ij}
-\frac{\lambda^2}{2}\left(
\lVert\mathbf r_{ij}\rVert_2^2-d_{act}^2\right),
\end{aligned}
\right.
\tag{10-1}
\]
```

#### 显示公式 094，\tag{10-2}（正文第 4460-4472 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf r_{ij}^T\left(
\mathbf a_{i}^{safe}-\mathbf a_{j}^{safe}\right)
\ge a_{ij,req},\\
&\mathbf a_i^{safe}=\mathbf a_i^{nom}+\Delta\mathbf a_i .
\end{aligned}
\right.
\tag{10-2}
\]
```

#### 显示公式 095，\tag{10-3}（正文第 4476-4489 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf p_i^{safe}=\mathbf p_i^{nom}+\Delta\mathbf p_i,\\
&\mathbf v_i^{safe}=\mathbf v_i^{nom}+
\frac{\Delta\mathbf p_i}{t_{lookahead}},\\
&\lVert\Delta\mathbf p_i\rVert_2\le0.5\,\mathrm m,\\
&\lVert\Delta\mathbf a_i\rVert_2\le1.5\,\mathrm{m/s^2}.
\end{aligned}
\right.
\tag{10-3}
\]
```

#### 显示公式 096，\tag{10-4}（正文第 4528-4533 行）

```latex
\[
\delta r=\lVert\mathbf r^{safe}-\mathbf r^{nom}\rVert_2.
\tag{10-4}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十一、感知与规划组件原理 > 11.1 FAST-LIO 状态估计

#### 显示公式 097，\tag{11-1}（正文第 4549-4555 行）

```latex
\[
\mathbf x=(\mathbf p,R,R_{LI},\mathbf t_{LI},\mathbf v,
\mathbf b_g,\mathbf b_a,\mathbf g),
\tag{11-1}
\]
```

#### 显示公式 098，\tag{11-2}（正文第 4559-4570 行）

```latex
\[
\left\{
\begin{aligned}
&\dot{\mathbf p}=\mathbf v,\\
&\dot R=R[\boldsymbol\omega_m-\mathbf b_g]_\times,\\
&\dot{\mathbf v}=R(\mathbf a_m-\mathbf b_a)+\mathbf g .
\end{aligned}
\right.
\tag{11-2}
\]
```

#### 显示公式 099，\tag{11-3}（正文第 4574-4585 行）

```latex
\[
\left\{
\begin{aligned}
&r_i=\mathbf n_i^T\!\left(
R(R_{LI}\mathbf p_i+\mathbf t_{LI})+\mathbf p-\mathbf q_i\right),\\
&\mathbf x^{+}=\mathbf x\boxplus K\bigl(\mathbf r-h(\mathbf x)\bigr).
\end{aligned}
\right.
\tag{11-3}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十一、感知与规划组件原理 > 11.2 FUEL 自主探索规划器

#### 显示公式 100，\tag{11-4}（正文第 4594-4605 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf p(t)=\sum_i\mathbf q_iB_{i,q}(t),\\
&J_{FUEL}=\lambda_sJ_{smooth}+\lambda_dJ_{distance}+
\lambda_fJ_{feasibility}+\lambda_vJ_{view}+\lambda_tJ_{time}.
\end{aligned}
\right.
\tag{11-4}
\]
```

#### 显示公式 101，\tag{11-5}（正文第 4609-4619 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf v_i=\frac{\mathbf q_{i+1}-\mathbf q_i}{\Delta t},\\
&\mathbf a_i=\frac{\mathbf q_{i+2}-2\mathbf q_{i+1}+\mathbf q_i}{\Delta t^2},
\end{aligned}
\right.
\tag{11-5}
\]
```

#### 显示公式 102，\tag{11-6}（正文第 4623-4630 行）

```latex
\[
J_{feasibility}=
\sum_{i,k}\left[\left(|v_{i,k}|-v_{max}\right)_+^2+
\left(|a_{i,k}|-a_{max}\right)_+^2\right].
\tag{11-6}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十一、感知与规划组件原理 > 11.3 Diff-Planner 局部轨迹优化

#### 显示公式 103，\tag{11-7}（正文第 4643-4649 行）

```latex
\[
J_{Diff}=J_{smooth}+\Phi_{obs}+\Phi_{swarm}+
\Phi_{feas}+J_{qvar}+J_{time} .
\tag{11-7}
\]
```

#### 显示公式 104，\tag{11-8}（正文第 4653-4669 行）

```latex
\[
\left\{
\begin{aligned}
&d_{ij,ell}^2=\frac{(z_i-z_j)^2}{2^2}+
\frac{(x_i-x_j)^2+(y_i-y_j)^2}{1^2},\\
&\Phi_{swarm}=\sum_{j\ne i}w_s
\left[D_{ij}^2-d_{ij,ell}^2\right]_+^3,\\
&D_{ij}=1.5\,(d_{swarm}+d_{j,des}),\\
&\Phi_{feas}\supset
\left[\lVert\cdot\rVert_2^2-\mathrm{limit}^2\right]_+^3,\\
&D_{check}=1.25\,(d_{swarm}+d_{j,des}).
\end{aligned}
\right.
\tag{11-8}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十二、OpenBlocks 障碍地图规划与多机执行 > 12.2 三机 OpenBlocks 可重构编队避障

#### 显示公式 105，\tag{12-1}（正文第 4761-4767 行）

```latex
\[
\underline{c}=\min_i\left(
c_i^{plan}-e_i^{track}\right),
\tag{12-1}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十三、px4ctrl C99 代码生成、可移植构建与 SIL 验证 > 13.4 SIL 一致性公式

#### 显示公式 106，\tag{13-1}（正文第 4892-4904 行）

```latex
\[
\left\{
\begin{aligned}
&\mathrm{RMSE}_{\Delta p}=
\sqrt{\frac{1}{N}\sum_{k=1}^{N}
\left\lVert\mathbf p^{(g)}_k-\mathbf p^{(c)}_k\right\rVert_2^2},\\
&e_{att,max}=\max_{k,j}|\theta^{(g)}_{k,j}-\theta^{(c)}_{k,j}|,
\end{aligned}
\right.
\tag{13-1}
\]
```

#### 显示公式 107，\tag{13-2}（正文第 4908-4913 行）

```latex
\[
e_{rotor,max}=\max_{k,i}|\omega^{(g)}_{k,i}-\omega^{(c)}_{k,i}| .
\tag{13-2}
\]
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十四、生成 C99 在 ROS1/Gazebo 的运行时闭环 > 14.1 运行时链路与后端识别

#### 显示公式 108，\tag{14-1}（正文第 5003-5013 行）

```latex
\[
\left\{
\begin{aligned}
&\mathbf p_{NED}=\begin{bmatrix}p_{y,N}\\p_{x,E}\\-p_{z,U}\end{bmatrix},\\
&{}^{W}\mathbf v=R_{W\leftarrow B}(q)\,{}^{B}\mathbf v.
\end{aligned}
\right.
\tag{14-1}
\]
```

## 二、行内公式

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 二、指标定义与负样本处理 > 2.3 参考轨迹与故障注入

#### 行内公式 001（正文第 168 行）

```latex
\(\mathbf v_r\)
```

#### 行内公式 002（正文第 168 行）

```latex
\(\mathbf a_r\)
```

#### 行内公式 003（正文第 168 行）

```latex
\(\mathbf p_r\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 二、指标定义与负样本处理 > 2.4 指标与有效通过判定

#### 行内公式 004（正文第 204 行）

```latex
\(N\)
```

#### 行内公式 005（正文第 247 行）

```latex
\(\pm5\%\)
```

#### 行内公式 006（正文第 248 行）

```latex
\(t_0=15\,\mathrm s\)
```

#### 行内公式 007（正文第 248 行）

```latex
\(t_{end}=45\,\mathrm s\)
```

#### 行内公式 008（正文第 266 行）

```latex
\(t_{end}\)
```

#### 行内公式 009（正文第 266 行）

```latex
\([t_0,t_{end}]\)
```

#### 行内公式 010（正文第 266 行）

```latex
\(t_k\)
```

#### 行内公式 011（正文第 267 行）

```latex
\(t_s\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 三、云纵150参照虚拟机体与参数 Profile > 3.2 坐标、旋翼与物理链

#### 行内公式 012（正文第 496 行）

```latex
\(p_{x,E}\)
```

#### 行内公式 013（正文第 496 行）

```latex
\(p_{y,N}\)
```

#### 行内公式 014（正文第 496 行）

```latex
\(p_{z,U}\)
```

#### 行内公式 015（正文第 496 行）

```latex
\(v_F\)
```

#### 行内公式 016（正文第 496 行）

```latex
\(v_L\)
```

#### 行内公式 017（正文第 496 行）

```latex
\(v_U\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 三、云纵150参照虚拟机体与参数 Profile > 3.3 公共动力学、执行器与实际 X 型分配

#### 行内公式 018（正文第 549 行）

```latex
\(\mathbf J_B\)
```

#### 行内公式 019（正文第 549 行）

```latex
\(i\)
```

#### 行内公式 020（正文第 566 行）

```latex
\(T_{0,i}\)
```

#### 行内公式 021（正文第 566 行）

```latex
\(T_i\)
```

#### 行内公式 022（正文第 583 行）

```latex
\(\omega_h\)
```

#### 行内公式 023（正文第 608 行）

```latex
\([0,\omega_{max}]\)
```

#### 行内公式 024（正文第 609 行）

```latex
\([-\omega_{max},0]\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 四、统一控制器接口与 FormalRunner 执行边界

#### 行内公式 025（正文第 654 行）

```latex
\(j\)
```

#### 行内公式 026（正文第 654 行）

```latex
\(\boldsymbol\chi_j\)
```

#### 行内公式 027（正文第 671 行）

```latex
\(\mathcal A_{b_j}\)
```

#### 行内公式 028（正文第 680 行）

```latex
\(T_s=0.01\,\mathrm{s}\)
```

#### 行内公式 029（正文第 680 行）

```latex
\(\mathcal D_{T_s}\)
```

#### 行内公式 030（正文第 713 行）

```latex
\(T_v=0.05\,\mathrm{s}\)
```

#### 行内公式 031（正文第 722 行）

```latex
\(T_v=0.05\,\mathrm{s}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 五、Official PID 工程基线

#### 行内公式 032（正文第 727 行）

```latex
\(K_p=1.5\)
```

#### 行内公式 033（正文第 728 行）

```latex
\(K_d=1\)
```

#### 行内公式 034（正文第 728 行）

```latex
\(K_p=8\)
```

#### 行内公式 035（正文第 728 行）

```latex
\(K_i=6\)
```

#### 行内公式 036（正文第 728 行）

```latex
\(K_d=4\)
```

#### 行内公式 037（正文第 831 行）

```latex
\(a_i\)
```

#### 行内公式 038（正文第 832 行）

```latex
\(d_i\)
```

#### 行内公式 039（正文第 834 行）

```latex
\(s_i\)
```

#### 行内公式 040（正文第 834 行）

```latex
\(\gamma\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.1 48 条控制器的正文登记与章节分工

#### 行内公式 041（正文第 852 行）

```latex
\(\mathbf e_p=\mathbf p_r-\mathbf p\)
```

#### 行内公式 042（正文第 852 行）

```latex
\(\mathbf e_v=\mathbf v_r-\mathbf v\)
```

#### 行内公式 043（正文第 852 行）

```latex
\(\mathbf a_r\)
```

#### 行内公式 044（正文第 852 行）

```latex
\(\operatorname{sat}_{[l,u]}(\cdot)\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > cascade_pid

#### 行内公式 045（正文第 892 行）

```latex
\(\mathbf a_c\)
```

#### 行内公式 046（正文第 892 行）

```latex
\(\boldsymbol\omega_c\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > gain_scheduled_pid

#### 行内公式 047（正文第 900 行）

```latex
\(\rho\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > fuzzy_pid

#### 行内公式 048（正文第 942 行）

```latex
\(\mu_\ell\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > neural_pid

#### 行内公式 049（正文第 966 行）

```latex
\(\boldsymbol\xi\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > fixed_awff_pid

#### 行内公式 050（正文第 1015 行）

```latex
\(u_{ff}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > fixed_awff_l1_residual

#### 行内公式 051（正文第 1039 行）

```latex
\(C(s)\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > fixed_awff_l1_indi

#### 行内公式 052（正文第 1062 行）

```latex
\(G^{\dagger}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.2 PID 族 > pid_awff_linear_eso

#### 行内公式 053（正文第 1070 行）

```latex
\(z_1,z_2,z_3\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族

#### 行内公式 054（正文第 1096 行）

```latex
\(\tilde{\mathbf x}\)
```

#### 行内公式 055（正文第 1096 行）

```latex
\(\tilde{\mathbf u}\)
```

#### 行内公式 056（正文第 1096 行）

```latex
\(\dot{\tilde{\mathbf x}}=A\tilde{\mathbf x}+B\tilde{\mathbf u}\)
```

#### 行内公式 057（正文第 1096 行）

```latex
\(\mathbf y=C\tilde{\mathbf x}\)
```

#### 行内公式 058（正文第 1096 行）

```latex
\(H_2/H_\infty\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > lqr_baseline

#### 行内公式 059（正文第 1119 行）

```latex
\(\mathbf a_c\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > lqi_baseline

#### 行内公式 060（正文第 1146 行）

```latex
\(T_s=0.01\,\mathrm s\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > lqg

#### 行内公式 061（正文第 1174 行）

```latex
\(L_p,L_v\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > h2_state_feedback

#### 行内公式 062（正文第 1182 行）

```latex
\(H_2\)
```

#### 行内公式 063（正文第 1182 行）

```latex
\(H_2\)
```

#### 行内公式 064（正文第 1199 行）

```latex
\(H_2\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > hinf_hover_wrench

#### 行内公式 065（正文第 1207 行）

```latex
\(H_\infty\)
```

#### 行内公式 066（正文第 1224 行）

```latex
\([0,25]\,\mathrm N\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.3 线性与鲁棒状态反馈族 > pole_placement_luenberger

#### 行内公式 067（正文第 1250 行）

```latex
\(K,L\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > backstepping_baseline

#### 行内公式 068（正文第 1279 行）

```latex
\(\operatorname{sat}_{\mathcal A}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > adaptive_backstepping

#### 行内公式 069（正文第 1303 行）

```latex
\(\hat{\mathbf d}\)
```

#### 行内公式 070（正文第 1303 行）

```latex
\(\Gamma\)
```

#### 行内公式 071（正文第 1303 行）

```latex
\(\boldsymbol\Phi\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > feedback_linearization

#### 行内公式 072（正文第 1328 行）

```latex
\(\ddot{\tilde{\mathbf e}}_p+K_d\dot{\tilde{\mathbf e}}_p+K_p\tilde{\mathbf e}_p=\mathbf 0\)
```

#### 行内公式 073（正文第 1328 行）

```latex
\(G(\mathbf x)\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > mrac

#### 行内公式 074（正文第 1377 行）

```latex
\(\boldsymbol\phi\)
```

#### 行内公式 075（正文第 1377 行）

```latex
\(\hat{\Theta}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.4 非线性与自适应控制族 > ndi

#### 行内公式 076（正文第 1385 行）

```latex
\(B(\mathbf x)\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族

#### 行内公式 077（正文第 1410 行）

```latex
\(\mathbf a_c\)
```

#### 行内公式 078（正文第 1410 行）

```latex
\(\mathbf s\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > integral_smc

#### 行内公式 079（正文第 1436 行）

```latex
\(\operatorname{sgn}(\mathbf s)\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > terminal_smc

#### 行内公式 080（正文第 1460 行）

```latex
\(\odot\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > adaptive_smc

#### 行内公式 081（正文第 1510 行）

```latex
\(\boldsymbol\delta\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > fuzzy_smc

#### 行内公式 082（正文第 1518 行）

```latex
\(K_f\)
```

#### 行内公式 083（正文第 1534 行）

```latex
\(\mathbf K_f(\mathbf s)\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.5 滑模控制族 > super_twisting_smc

#### 行内公式 084（正文第 1558 行）

```latex
\(\mathbf z\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式

#### 行内公式 085（正文第 1589 行）

```latex
\(\mathbf x_{i|k}\)
```

#### 行内公式 086（正文第 1589 行）

```latex
\(k\)
```

#### 行内公式 087（正文第 1589 行）

```latex
\(i\)
```

#### 行内公式 088（正文第 1589 行）

```latex
\(\mathbf U_k\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > robust_mpc

#### 行内公式 089（正文第 1622 行）

```latex
\(\max\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > adaptive_mpc

#### 行内公式 090（正文第 1664 行）

```latex
\(\mathcal I(\cdot)\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > tube_mpc

#### 行内公式 091（正文第 1690 行）

```latex
\(\mathbf v\)
```

#### 行内公式 092（正文第 1690 行）

```latex
\(\mathbf z\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > mppi

#### 行内公式 093（正文第 1763 行）

```latex
\(S_{\min}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > fixed_linear_mpc_l1_indi

#### 行内公式 094（正文第 1831 行）

```latex
\(C(s)\)
```

#### 行内公式 095（正文第 1831 行）

```latex
\(G^{\dagger}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.6 预测与优化控制的 10 条公式 > fixed_qp_nmpc_l1_indi_cbf

#### 行内公式 096（正文第 1858 行）

```latex
\(h\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > se3_basic

#### 行内公式 097（正文第 1870 行）

```latex
\(SE(3)\)
```

#### 行内公式 098（正文第 1870 行）

```latex
\(\tilde{\mathbf e}_p=\mathbf p-\mathbf p_r\)
```

#### 行内公式 099（正文第 1870 行）

```latex
\(\tilde{\mathbf e}_v=\mathbf v-\mathbf v_r\)
```

#### 行内公式 100（正文第 1890 行）

```latex
\(\mathbf e_p=\mathbf p_r-\mathbf p\)
```

#### 行内公式 101（正文第 1890 行）

```latex
\(\mathbf e_v=\mathbf v_r-\mathbf v\)
```

#### 行内公式 102（正文第 1890 行）

```latex
\(\mathbf M_c\)
```

#### 行内公式 103（正文第 1908 行）

```latex
\(c_\phi,c_\theta,c_T\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > dfbc_basic

#### 行内公式 104（正文第 1938 行）

```latex
\(q_0=0.02\)
```

#### 行内公式 105（正文第 1938 行）

```latex
\(k_d=-0.4\)
```

#### 行内公式 106（正文第 1938 行）

```latex
\(\pm4\ \mathrm{m/s^2}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > dfbc_smooth_robust_attitude

#### 行内公式 107（正文第 1946 行）

```latex
\(\tanh\)
```

#### 行内公式 108（正文第 1969 行）

```latex
\((\mathbf s_k-\mathbf s_{k-1})/T_s\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > dfbc_smooth_robust_bodyrate

#### 行内公式 109（正文第 2011 行）

```latex
\(\omega_{r,z}=0\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.7 几何与微分平坦控制的 6 条公式 > dfbc_high_order_attitude

#### 行内公式 110（正文第 2050 行）

```latex
\(\dot{\mathbf s}^{\Delta}_k\)
```

#### 行内公式 111（正文第 2050 行）

```latex
\(\mathbf p_r^{(3)}\)
```

#### 行内公式 112（正文第 2050 行）

```latex
\(\mathbf p_r^{(4)}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 六、七个算法族 46 条控制器的图形化建模与统一实现 > 6.8 学习控制的 2 条公式 > trained_neural_residual

#### 行内公式 113（正文第 2168 行）

```latex
\(b_{\mathrm{fb},k}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 八、px4ctrl 图形化设计与 MWORKS 全机验证

#### 行内公式 114（正文第 4060 行）

```latex
\(\mathbf a_r\)
```

#### 行内公式 115（正文第 4062 行）

```latex
\(K_p=K_v=1.5\)
```

#### 行内公式 116（正文第 4064 行）

```latex
\(+g\)
```

#### 行内公式 117（正文第 4070 行）

```latex
\(\mathbf a_c=\mathbf a_r+K_p\mathbf e_p+K_v\mathbf e_v\)
```

#### 行内公式 118（正文第 4071 行）

```latex
\(\mathbf a_d=\mathbf a_c+[0,0,g]^T\)
```

#### 行内公式 119（正文第 4071 行）

```latex
\(T_c=ma_{d,z}\)
```

#### 行内公式 120（正文第 4072 行）

```latex
\(K_p=K_v=1.5\)
```

#### 行内公式 121（正文第 4092 行）

```latex
\(K_p=K_v=1.5\)
```

#### 行内公式 122（正文第 4135 行）

```latex
\(\psi\)
```

#### 行内公式 123（正文第 4167 行）

```latex
\(\psi\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 九、Official PID 与 px4ctrl 七场景对比与灵敏度验证 > 9.1 七场景核心对比

#### 行内公式 124（正文第 4301 行）

```latex
\(t_0=15\,\mathrm s\)
```

#### 行内公式 125（正文第 4301 行）

```latex
\(t_{end}=45\,\mathrm s\)
```

#### 行内公式 126（正文第 4301 行）

```latex
\(\pm5\%\)
```

#### 行内公式 127（正文第 4316 行）

```latex
\(\pm5\%\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 九、Official PID 与 px4ctrl 七场景对比与灵敏度验证 > 9.2 px4ctrl 性能结果与 Official PID 基线特征

#### 行内公式 128（正文第 4322 行）

```latex
\(K_p=1.5\)
```

#### 行内公式 129（正文第 4322 行）

```latex
\(K_d=1\)
```

#### 行内公式 130（正文第 4322 行）

```latex
\(K_p=8\)
```

#### 行内公式 131（正文第 4322 行）

```latex
\(K_i=6\)
```

#### 行内公式 132（正文第 4322 行）

```latex
\(K_d=4\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十、三机编队 Figure8 与 ECBF 安全参考调节 > 10.1 三机 Figure8 编队结果

#### 行内公式 133（正文第 4401 行）

```latex
\(10^{-13}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十、三机编队 Figure8 与 ECBF 安全参考调节 > 10.2 三机 ECBF 安全参考调节

#### 行内公式 134（正文第 4491 行）

```latex
\(d_{act}=1.5\,\mathrm m\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十一、感知与规划组件原理 > 11.1 FAST-LIO 状态估计

#### 行内公式 135（正文第 4557 行）

```latex
\(R_{LI},\mathbf t_{LI}\)
```

#### 行内公式 136（正文第 4587 行）

```latex
\(r_i\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十一、感知与规划组件原理 > 11.2 FUEL 自主探索规划器

#### 行内公式 137（正文第 4607 行）

```latex
\(\mathbf q_i\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十二、OpenBlocks 障碍地图规划与多机执行 > 12.2 三机 OpenBlocks 可重构编队避障

#### 行内公式 138（正文第 4770 行）

```latex
\(\{0.4466,\,0.4483,\,0.4459\}\,\mathrm m\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十三、px4ctrl C99 代码生成、可移植构建与 SIL 验证 > 13.4 SIL 一致性公式

#### 行内公式 139（正文第 4890 行）

```latex
\(\mathbf p^{(g)}\)
```

#### 行内公式 140（正文第 4890 行）

```latex
\(\mathbf p^{(c)}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十四、生成 C99 在 ROS1/Gazebo 的运行时闭环

#### 行内公式 141（正文第 4960 行）

```latex
\(10^{-13}\)
```

### 基于 MWORKS 的四旋翼位姿控制全链路仿真平台 > 十四、生成 C99 在 ROS1/Gazebo 的运行时闭环 > 14.3 运行时稳态跟踪结果

#### 行内公式 142（正文第 5069 行）

```latex
\(10^{-13}\)
```
