# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a simple interactive visualization project containing a single HTML file with embedded CSS and JavaScript. The project consists of:

- `interactive_visualization/interactive_visualization.html` - A complete HTML5 canvas-based particle system visualization

## Running the Project

To view the visualization:
- Open `interactive_visualization/interactive_visualization.html` directly in any modern web browser
- Or use `start interactive_visualization/interactive_visualization.html` on Windows

## Architecture

The visualization is built as a self-contained HTML file with:

- **Canvas Rendering**: Uses HTML5 Canvas API with 2D context for particle rendering
- **Animation Loop**: Uses `requestAnimationFrame` for smooth 60fps animation
- **Particle System**: Object-oriented particle class with physics simulation including:
  - Position and velocity vectors
  - Life cycle with decay over time
  - Collision detection with canvas boundaries
  - Optional gravity effects
- **Interactive Controls**: Button-based UI for particle manipulation and physics toggles
- **Real-time Stats**: Live display of particle count, FPS, and physics state
- **Color Theming**: Multiple predefined color palettes that can be switched dynamically

The particle system automatically generates new particles to maintain continuous animation, with a maximum limit of 100 particles to maintain performance.

## Development Notes

- The project uses vanilla JavaScript with ES6 classes
- Canvas rendering is optimized with alpha blending for particle trails
- Mouse interactions spawn particles on click and movement
- All styling uses CSS3 with glassmorphism effects and gradients