#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import time

def mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter):
    """
    Compute the Mandelbrot set for the given range and resolution.
    
    Parameters:
        xmin, xmax: Real axis boundaries.
        ymin, ymax: Imaginary axis boundaries.
        width, height: Resolution of the grid.
        max_iter: Maximum number of iterations.
    
    Returns:
        A 2D NumPy array with the iteration count for each point.
    """
    # Create a grid of complex numbers
    real = np.linspace(xmin, xmax, width)
    imag = np.linspace(ymin, ymax, height)
    c = real[np.newaxis, :] + 1j * imag[:, np.newaxis]
    
    z = np.zeros_like(c, dtype=np.complex128)
    output = np.zeros(c.shape, dtype=int)
    
    # Mask to track points that haven't diverged
    mask = np.full(c.shape, True, dtype=bool)
    
    for i in range(max_iter):
        # Only update points that have not diverged yet
        z[mask] = z[mask]**2 + c[mask]
        # Find points that have just diverged
        diverged = np.abs(z) > 2
        just_diverged = diverged & mask
        output[just_diverged] = i
        mask[diverged] = False
    # For points that never diverged, set iteration count to max_iter
    output[mask] = max_iter
    return output

def main():
    start_time = time.time()
    
    # Parameters for ~6 seconds Mandelbrot computation:
    #width, height = 800, 600
    #max_iter = 1000
    #xmin, xmax = -2.0, 1.0
    #ymin, ymax = -1.0, 1.0
    # Parameters for ~1 minute Mandelbrot computation:
    width, height = 1200, 900
    max_iter = 5000
    xmin, xmax = -2.0, 1.0
    ymin, ymax = -1.0, 1.0

    print("Computing Mandelbrot set...")
    mandelbrot = mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter)
    
    # Plot and save the Mandelbrot set image
    plt.imshow(mandelbrot, cmap='hot', extent=(xmin, xmax, ymin, ymax))
    plt.colorbar()
    plt.title("Mandelbrot Set")
    plt.savefig("mandelbrot.png")
    print("Mandelbrot set computed and saved as 'mandelbrot.png'")
    print(f"Time elapsed: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()

