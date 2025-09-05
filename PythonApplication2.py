import turtle
import math

def setup_turtle():
    """Initialize turtle settings"""
    t = turtle.Turtle()
    t.speed(0)  # Fastest speed
    t.penup()
    t.hideturtle()
    return t

def draw_modified_edge(t, length, depth):
    """
    Recursively draw an edge with the pattern:
    1. Divide edge into three equal segments
    2. Replace middle segment with two sides of an equilateral triangle pointing INWARD
    3. This creates four smaller edges from one original edge
    """
    if depth == 0:
        # Base case: just draw a straight line
        t.forward(length)
    else:
        # Calculate the length of each segment (1/3 of original)
        segment_length = length / 3.0
        
        # Draw first segment (recursively)
        draw_modified_edge(t, segment_length, depth - 1)
        
        # Turn RIGHT to create an INWARD-pointing triangle
        t.right(60)
        draw_modified_edge(t, segment_length, depth - 1)
        
        # Turn LEFT to complete the triangle
        t.left(120)
        draw_modified_edge(t, segment_length, depth - 1)
        
        # Turn RIGHT to return to original direction
        t.right(60)
        
        # Draw the final segment (recursively)
        draw_modified_edge(t, segment_length, depth - 1)

def draw_polygon_with_pattern(t, num_sides, side_length, depth):
    """Draw a polygon with the pattern applied to each side"""
    # Calculate the interior angle of the polygon
    interior_angle = 180 * (num_sides - 2) / num_sides
    turn_angle = 180 - interior_angle
    
    for _ in range(num_sides):
        draw_modified_edge(t, side_length, depth)
        t.right(turn_angle)

def main():
    """Main function to get user input and draw the pattern"""
    # Set up the screen
    screen = turtle.Screen()
    screen.title("Geometric Pattern Generator")
    screen.bgcolor("white")
    screen.setup(width=600, height=600)
    
    # Get user input
    num_sides = int(screen.numinput("Number of sides", 
                                   "Enter the number of sides (3 or more):", 
                                   default=4, minval=3))
    side_length = int(screen.numinput("Side length", 
                                     "Enter the side length in pixels:", 
                                     default=300, minval=50))
    depth = int(screen.numinput("Recursion depth", 
                               "Enter the recursion depth:", 
                               default=2, minval=0, maxval=5))
    
    # Set up the turtle
    t = setup_turtle()
    
    # Position the turtle to center the drawing
    t.penup()
    
    # Calculate starting position based on polygon size
    # For regular polygons, the radius is: side_length / (2 * sin(π/num_sides))
    radius = side_length / (2 * math.sin(math.pi / num_sides))
    
    # Adjust starting position for square to make it centered properly
    if num_sides == 4:
        t.goto(-side_length/2, -side_length/2)
        t.setheading(0)  # Start facing right
    else:
        t.goto(0, -radius)  # Start at the bottom for other polygons
        # Set initial orientation based on number of sides
        if num_sides % 2 == 0:
            t.setheading(90 - (180 / num_sides))
        else:
            t.setheading(90)
    
    t.pendown()
    
    # Draw the pattern
    t.color("black")
    t.begin_fill()
    draw_polygon_with_pattern(t, num_sides, side_length, depth)
    t.end_fill()
    
    # Keep the window open until clicked
    screen.exitonclick()

if __name__ == "__main__":
    main()
