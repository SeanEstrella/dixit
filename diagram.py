from graphviz import Digraph

# Create a Digraph object
dot = Digraph(comment='AI in Dixit: How the Bot Works')

# Set the graph attributes
dot.attr(rankdir='LR', fontname='Proxima Nova', fontsize='12')  # Left to Right orientation with consistent font style

# Add nodes for the Storytelling track with adjusted colors and styles
dot.node('Start', 'AI Bot', shape='ellipse', style='filled', fillcolor='#A7D3F2')  # Light blue for the starting point
dot.node('GenerateClue', 'Generate Clue (GPT-4)\n[Lightbulb]', shape='rectangle', style='filled', fillcolor='#A1E3A1')  # Light green
dot.node('ObfuscateClue', 'Obfuscate Clue (GPT-4)', shape='rectangle', style='filled', fillcolor='#A1E3A1')  # Light green

# Add nodes for the Guessing track
dot.node('ProcessImages', 'Process Images (OpenCLIP)\n[Camera]', shape='rectangle', style='filled', fillcolor='#F4A7A3')  # Light coral
dot.node('CompareClues', 'Compare Clues and Images', shape='rectangle', style='filled', fillcolor='#F4A7A3')  # Light coral

# Add edges to connect the nodes for storytelling
dot.edge('Start', 'GenerateClue', label='Storytelling Track', fontsize='10', fontcolor='black', arrowsize='0.7')
dot.edge('GenerateClue', 'ObfuscateClue', fontsize='10', fontcolor='black', arrowsize='0.7')

# Add edges to connect the nodes for guessing
dot.edge('Start', 'ProcessImages', label='Guessing Track', fontsize='10', fontcolor='black', arrowsize='0.7')
dot.edge('ProcessImages', 'CompareClues', fontsize='10', fontcolor='black', arrowsize='0.7')

# Create a legend node for clarity
dot.node('Legend', 'Legend:\n[Lightbulb]: Clue Generation\n[Camera]: Image Processing', shape='box', style='dashed', fontsize='10', fontcolor='black', fillcolor='white', width='1.5')

# Position the legend closer to the diagram
dot.attr(labeljust='l', labelloc='b', fontsize='10')

# Render the graph to a file (e.g., in PNG format)
dot.render('ai_in_dixit_bot', format='png', cleanup=False)

# Display the Graphviz source code (optional)
print(dot.source)
