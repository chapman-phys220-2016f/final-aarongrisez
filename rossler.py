#!usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numba as nb
from mpl_toolkits.mplot3d import Axes3D

"""
Module to investigate behavior of Rossler oscillator
"""

@nb.jit
def rossler(c, T=500.0, dt=0.001):
    """
    Parameters:
    -----------
        c: float
            tunable parameter we are investigating in this module
        T: float
            total time for running the simulation
        dt: float
            mesh spacing for rk4 solutions

    Returns:
    --------
        pd.Dataframe
            4 series pd.Dataframe containing a series of time points and the 3 dimensional solution for the simulation
    """
    n = int(T / dt) #Number of mesh points
    t_vals = np.linspace(0, T, n)
    x = np.zeros(n)
    y = np.zeros(n)
    z = np.zeros(n)
    u_p = np.array([x,y,z])
    u = np.transpose(u_p)
    soln_p = integrate(u, dt, n, c)
    soln = np.transpose(soln_p)
    df = pd.DataFrame({"t":t_vals, "x":soln[0], "y":soln[1], "z":soln[2]})
    indexed_df = df.set_index(t_vals)
#    c_string = str(c)
#    c_string = c_string.replace('.','_') #Removes periods for filenames
#    indexed_df.to_csv('c_equals_' + c_string)
    return indexed_df

@nb.jit
def du(m, c):
    """
    Vector Differential Equation for Rossler Attractor

    Parameters:
    -----------
        m: array
            previous mesh point solution
        c: float
            current c value

    Returns:
        array
            array representing differential equations evaluated at previous mesh point 
    """
    a = 0.2
    b = 0.2
    return np.array((-m[1] - m[2], m[0] + a * m[1], b + m[2] * (m[0] - c)))     #First component is x, second component is y, third component is z

def integrate(u, delta_t, n, c):
    """
    Implements rk4 step to solve Rossler Attractor problem

    Parameters:
    -----------
        u: array
            initialized solutions array
        delta_t: float
            time step to use in solution mesh
        n: int
            number of mesh points
        c: float
            current c value

    Returns:
    --------
        array (n, 3)
            solution meshes for all 3 dimensions of Rossler Attractor
    """
    a = 0.2
    b = 0.2
    @nb.jit
    def rk4_step(u_prev, delta_t, t_current):
        K1 = delta_t * du(u_prev, c)
        K2 = delta_t * du(u_prev + K1 / 2, c)
        K3 = delta_t * du(u_prev + K2 / 2, c)
        K4 = delta_t * du(u_prev + K3, c)# 4 intermediate approximations
        return u_prev + (K1 + 2 * K2 + 2 * K3 + K4) / 6
    @nb.jit
    def for_loop(u, delta_t, n):
        for i in range(n):
            t_current = delta_t * i
            u[i] = rk4_step(u[i - 1], delta_t, t_current)
        return u
    return for_loop(u, delta_t, n)

def plotxyz_separate(sol):
    """
    Plots 3 parametric plots for x, y, and z

    Parameters:
    -----------
        sol: pd.Dataframe
            solution meshes computed earlier

    Returns:
    --------
        none
    """
    plots = plt.figure(1, figsize=(12,4))
    plx = plots.add_subplot(1,3,1)
    plotx(sol, plx)
    ply = plots.add_subplot(1,3,2)
    ploty(sol, ply)
    plz = plots.add_subplot(1,3,3)
    plotz(sol, plz)

def plotx(sol, plotx):
    """
    Plots single solution plot

    Parameters:
    -----------
        sol: pd.Dataframe
            solution mesh computed earlier
        plotx: matplotlib.pyplot.subplot
            subplot to use in plotxyz_separate()

    Returns:
    --------
        none
    """
    plotx.set_title("$X$ versus $t$ Plot")
    plotx.set_xlabel("time ($s$)")
    plotx.set_ylabel("position ($m$)")
    plotx.set_ylim((-12,12))
    plotx.plot(sol['t'], sol['x'], 'k-', lw=0.5)

def ploty(sol, ploty):
    """
    Plots single solution plot

    Parameters:
    -----------
        sol: pd.Dataframe
            solution mesh computed earlier
        ploty: matplotlib.pyplot.subplot
            subplot to use in plotxyz_separate()

    Returns:
    --------
        none
    """
    ploty.set_title("$Y$ versus $t$ Plot")
    ploty.set_xlabel("time ($s$)")
    ploty.set_ylabel("position ($m$)")
    ploty.set_ylim((-12,12))
    ploty.plot(sol['t'], sol['y'], 'k-', lw=0.5)

def plotz(sol, plotz):
    """
    Plots single solution plot

    Parameters:
    -----------
        sol: pd.Dataframe
            solution mesh computed earlier
        plotz: matplotlib.pyplot.subplot
            subplot to use in plotxyz_separate()

    Returns:
    --------
        none
    """
    plotz.set_title("$Z$ versus $t$ Plot")
    plotz.set_xlabel("time ($s$)")
    plotz.set_ylabel("position ($m$)")
    plotz.set_ylim((0,25))
    plotz.plot(sol['t'], sol['z'], 'k-', lw=0.5)

def plot_2D_phase(sol, T0=100):
    """
    Plots 2D parametric plot

    Parameters:
    -----------
        sol: pd.Dataframe
            solution mesh computed earlier
        T0: int
            time index for transient points, this plot will ignore points with a lower time index

    Returns:
    --------
        none
    """
    sol_slice = sol[sol['t'] >= T0]
    plots = plt.figure(2, figsize=(12,5))
    plxy = plots.add_subplot(1,3,1)
    plotxy(sol_slice, T0, plxy)
    plyz = plots.add_subplot(1,3,2)
    plotyz(sol_slice, T0, plyz)
    plxz = plots.add_subplot(1,3,3)
    plotxz(sol_slice, T0, plxz)

def plotxy(sol, T0, fig):
    fig.set_title("$xy$ Parametric Plot")
    fig.set_xlabel("$x$ Position ($m$)")
    fig.set_ylabel("$y$ Position ($m$)")
    fig.scatter(sol['x'], sol['y'], s=.001, marker='.')

def plotyz(sol, T0, fig):
    fig.set_title("$yz$ Parametric Plot")
    fig.set_xlabel("$y$ Position ($m$)")
    fig.set_ylabel("$z$ Position ($m$)")
    fig.scatter(sol['y'], sol['z'], s=.001, marker='.')

def plotxz(sol, T0, fig):
    fig.set_title("$xz$ Parametric Plot")
    fig.set_xlabel("$x$ Position ($m$)")
    fig.set_ylabel("$z$ Position ($m$)")
    fig.scatter(sol['x'], sol['z'], s=.001, marker='.')

def plotxyz(sol, T0=100):
    """
    Plots 3D parametric plots of x, y, and z

    Parameters:
    -----------
        sol: pd.Dataframe
            solution mesh computed earlier
        T0: int
            time index for transient points, this plot will ignore points with a lower time index

    Returns:
    --------
        none
    """
    sol_slice = sol[sol['t'] >= T0]
    plot = plt.figure(3, figsize=(12,7),)
    xyz = plot.add_subplot(111, projection='3d')
    xyz.set_xlabel("$x$ Position")
    xyz.set_ylabel("$y$ Position")
    xyz.set_zlabel("$z$ Position")
    xyz.set_title("$xyz$ Parametric Plot")
    xyz.scatter(sol_slice['x'], sol_slice['y'], sol_slice['z'], s=.001, marker='.')

def test_rossler():
    test = type(rossler(1))
    case = type(pd.DataFrame([1,3,1]))
    assert test == case
