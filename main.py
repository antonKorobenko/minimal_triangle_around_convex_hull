import time
from tkinter import *
from random import randint
from random import uniform
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import time

MAX_CNT_RANDOM = 1000
MAX_CLICK_LENGTH = 0.1
global points, points_by_x, points_by_y, polygon
used_time = []


def onclick():
    ax.time_onclick = time.time()


def onrelease(event):
    if event.inaxes == ax:
        if event.button == 1 and ((time.time() - ax.time_onclick) < MAX_CLICK_LENGTH):
            points.append([event.xdata, event.ydata])
            ax.scatter(event.xdata, event.ydata, marker="o", color="#000000")
            ax.figure.canvas.draw()


def clear(save_points=True):
    global points
    if not save_points:
        points = []

    plt.cla()
    text.delete(1.0, END)
    plt.xlim(xmin * scale_factor, xmax * scale_factor)
    plt.ylim(ymin * scale_factor, ymax * scale_factor)

    ax.set(xlabel="x", ylabel="y", title="")
    ax.figure.canvas.draw()


def clear_all():
    clear(save_points=False)


def generate_rand_points():
    rand_n = int(rand_input.get())
    random(rand_n)


def random(manual_n=None):
    global points_by_x, points_by_y
    cnt_rand = MAX_CNT_RANDOM
    if not manual_n is None:
        cnt_rand = manual_n

    clear_all()
    points_by_x = []
    points_by_y = []
    for i in range(cnt_rand):
        x = uniform(-100, 100)
        y = uniform(-100, 100)
        # x = randint(-100, 100)
        # y = randint(-100, 100)
        points_by_x.append(x)
        points_by_y.append(y)
        add_new_point(x, y)
    ax.plot(points_by_x, points_by_y, "bo")
    ax.figure.canvas.draw()


def add_new_point(x, y):
    points.append([x, y])


def rotate(a, b, c):
    return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])


# using graham algorithm
def build_polygon():
    start = time.time()
    global polygon
    A = points
    n = len(A)  # number of points
    P = [i for i in range(n)]  # array of points
    for i in range(1, n):
        if A[P[i]][0] < A[P[0]][0]:  # if point P[i] on the left from point P[0]
            P[i], P[0] = P[0], P[i]  # swap indexes
    for i in range(2, n):  # insertion sort
        j = i
        while j > 1 and (rotate(A[P[0]], A[P[j - 1]], A[P[j]]) < 0):
            P[j], P[j - 1] = P[j - 1], P[j]
            j -= 1
    S = [P[0], P[1]]  # create a stack
    for i in range(2, n):
        while rotate(A[S[-2]], A[S[-1]], A[P[i]]) < 0:
            del S[-1]  # pop(S)
        S.append(P[i])  # push(S,P[i])

    res = [A[i] for i in S]
    res.append(res[0])  # add first point again to finish hull
    px = [i[0] for i in res]
    py = [i[1] for i in res]

    end = time.time()

    str_ans = (f"Points in hull >>\n {len(res)}\n"
               + f"Duration >>\n {(end - start):.5f}")
    text.delete(1.0, END)
    text.insert(INSERT, str_ans)

    ax.plot(px, py, color="red")
    ax.figure.canvas.draw()
    polygon = res


def intersection(a, b, c, d):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    x3 = c[0]
    y3 = c[1]
    x4 = d[0]
    y4 = d[1]

    if (y2 - y1) != 0:
        q = (x2 - x1) / (y1 - y2)
        sn = (x3 - x4) + (y3 - y4) * q
        if not sn:
            return None
        fn = (x3 - x1) + (y3 - y1) * q
        n = fn / sn

    else:
        if not (y3 - y4):
            return 0
        n = (y3 - y1) / (y3 - y4)
    x = x3 + (x4 - x3) * n
    y = y3 + (y4 - y3) * n
    return [x, y]


def getA(x1, y1, x2, y2):
    return -1 * (x1 * y2 - x1 * y1) / (x2 - x1) + y1


def getK(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1)


def getTrianglePoints(p11, p12, p21, p22, p):
    a1 = getA(p11[0], p11[1], p12[0], p12[1])
    k1 = getK(p11[0], p11[1], p12[0], p12[1])
    a2 = getA(p21[0], p21[1], p22[0], p22[1])
    k2 = getK(p21[0], p21[1], p22[0], p22[1])
    x2 = (2 * p[1] - 2 * k1 * p[0] - a1 - a2) / (k2 - k1)
    x1 = 2 * p[0] - x2
    y1 = k1 * x1 + a1
    y2 = k2 * x2 + a2

    return [x1, y1, x2, y2]


def sign(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


def isPointInTriangle(triangle, p):
    v1 = [triangle[0], triangle[1]]
    v2 = [triangle[2], triangle[3]]
    v3 = [triangle[4], triangle[5]]
    d1 = sign(p, v1, v2)
    d2 = sign(p, v2, v3)
    d3 = sign(p, v3, v1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_pos and has_neg)


def S(triangle):
    x1 = triangle[0]
    y1 = triangle[1]
    x2 = triangle[2]
    y2 = triangle[3]
    x3 = triangle[4]
    y3 = triangle[5]
    return abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2


def build_triangle():
    tr_p_x = [0, 0, 0]
    tr_p_y = [0, 0, 0]
    s = False
    start = time.time()

    for a in range(len(polygon) - 1):
        for b in range(len(polygon) - 1):
            if a != b:
                intersectionAB = intersection(polygon[a], polygon[a + 1], polygon[b], polygon[b + 1])
                if intersectionAB:
                    for c in range(len(polygon)):
                        if c != a and c != b and c != a + 1 and c != b + 1:
                            trianglePoints = getTrianglePoints(polygon[a], polygon[a + 1],
                                                               polygon[b], polygon[b + 1],
                                                               polygon[c])
                            trianglePoints.append(intersectionAB[0])
                            trianglePoints.append(intersectionAB[1])
                            x1 = format(trianglePoints[0], ".2f")
                            x2 = format(trianglePoints[2], ".2f")
                            x3 = format(trianglePoints[3], ".2f")
                            isAllPointsInTriangle = True
                            for i in polygon:
                                if not isPointInTriangle(trianglePoints, i):
                                    isAllPointsInTriangle = False
                            if isAllPointsInTriangle and x1 and x2 and x3:
                                if not s or s > S(trianglePoints):
                                    tr_p_x[0] = trianglePoints[0]
                                    tr_p_x[1] = trianglePoints[2]
                                    tr_p_x[2] = trianglePoints[4]
                                    tr_p_y[0] = trianglePoints[1]
                                    tr_p_y[1] = trianglePoints[3]
                                    tr_p_y[2] = trianglePoints[5]
                                    s = S(trianglePoints)
    end = time.time()
    str_ans = (f"Duration of building triangle >>\n {(end - start):.5f}" + f"\nArea of triangle >> \n{s}")
    text.delete(1.0, END)
    text.insert(INSERT, str_ans)
    tr_p_x.append(tr_p_x[0])
    tr_p_y.append(tr_p_y[0])
    ax.plot(tr_p_x, tr_p_y, color="black")
    ax.figure.canvas.draw()


if __name__ == "__main__":
    window = Tk()
    window.title("Lab")
    window.geometry("1500x9000")

    clear_button = Button(master=window, height=2, width=10, text="Clear", command=clear_all)
    rand_input = Entry(master=window, width=10, font=60)
    rand_generate_button = Button(master=window, height=2, width=30, text="Generate random points",
                                  command=generate_rand_points)
    build_button = Button(master=window, height=2, width=30, text="Build convex polygon", command=build_polygon)
    triangle_button = Button(master=window, height=2, width=30, text="Build triangle", command=build_triangle)

    scale_factor = 1
    text = Text(window)
    text.insert(INSERT, "")
    text.place(x=1050, y=48, height=900, width=300)
    xmin, xmax = -100, 100
    ymin, ymax = -100, 100
    fig, ax = plt.subplots(figsize=(10, 9))

    plt.xlim(xmin * scale_factor, xmax * scale_factor)
    plt.ylim(ymin * scale_factor, ymax * scale_factor)

    ax.set(xlabel="x", ylabel="y", title="")

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.mpl_connect("button_press_event", lambda event: onclick())
    canvas.mpl_connect("button_release_event", lambda event: onrelease(event))
    canvas.get_tk_widget().place(x=0, y=50)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()

    clear_button.place(x=0, y=0)
    rand_input.place(x=100, y=0)
    rand_generate_button.place(x=200, y=0)
    build_button.place(x=450, y=0)
    triangle_button.place(x=700, y=0)
    window.mainloop()
