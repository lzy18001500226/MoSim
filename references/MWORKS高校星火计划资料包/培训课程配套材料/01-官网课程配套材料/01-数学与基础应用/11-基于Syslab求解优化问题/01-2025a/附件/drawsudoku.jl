function drawSudoku(B)
    figure()
    hold("on")
    rectangle(position=[0 0 9 9], linewidth=3)
    rectangle(position=[3 0 3 9], linewidth=2)
    rectangle(position=[0 3 9 3], linewidth=2)
    rectangle(position=[0 1 9 1], linewidth=1)
    rectangle(position=[0 4 9 1], linewidth=1)
    rectangle(position=[0 7 9 1], linewidth=1)
    rectangle(position=[1 0 1 9], linewidth=1)
    rectangle(position=[4 0 1 9], linewidth=1)
    rectangle(position=[7 0 1 9], linewidth=1)

    if size(B, 2) == 9
        SM, SN = meshgrid2(1:9)
        B = [SN[:] SM[:] B[:]]
    end

    for ii = 1:size(B, 1)
        text(B[ii, 2] - 0.5, 9.5 - B[ii, 1], string(B[ii, 3]); horizontalalignment = "center")
    end
    hold("off")
    axis("equal")



end


B = [1 2 2;
    1 5 3;
    1 8 4;
    2 1 6;
    2 9 3;
    3 3 4;
    3 7 5;
    4 4 8;
    4 6 6;
    5 1 8;
    5 5 1;
    5 9 6;
    6 4 7;
    6 6 5;
    7 3 7;
    7 7 6;
    8 1 4;
    8 9 8;
    9 2 3;
    9 5 4;
    9 8 2];

drawSudoku(B)


