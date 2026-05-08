G = tf([.5 1.3],[1 1.2  1.6 0]);
T = feedback(G,1);
pole(T)
rlocus(G)
bode(G), grid
step(T), title('Closed-loop response for k=1')
step(feedback(2*G,1)), title('Closed-loop response for k=2')
G = tf(20,[1 7]) * tf([1 3.2 7.2],[1 -1.2 0.8]) * tf([1 -8 400],[1 33 700]);
T = feedback(G,1);
step(T), title('Closed-loop response for k=1')
bode(G), grid
k1 = 2;     T1 = feedback(G*k1,1);
k2 = 1/2;   T2 = feedback(G*k2,1);
step(T,'b',T1,'r',T2,'g',12), 
legend('k = 1','k = 2','k = 0.5')

