from graphviz import Digraph

# Creating a diagram for Image Recognition using OpenCLIP
diagram = Digraph('ImageRecognition', format='png')
diagram.attr(rankdir='LR', size='8,5')

# Defining styles for different types of nodes
diagram.attr('node', shape='ellipse', style='filled', color='pink', fontcolor='black')
diagram.node('A', 'Input: Dixit Card Image')

diagram.attr('node', shape='box', style='filled', color='lightblue', fontcolor='black')
diagram.node('B', 'Load Image')
diagram.node('C', 'Convert Image to RGB Format')
diagram.node('D', 'Prepare Image Tensor')
diagram.node('E', 'Apply Model Transformation')
diagram.node('F', 'Generate Caption using OpenCLIP')

diagram.attr('node', shape='ellipse', style='filled', color='pink', fontcolor='black')
diagram.node('G', 'Output: Descriptive Caption')

# Defining edges between nodes
diagram.edge('A', 'B')
diagram.edge('B', 'C')
diagram.edge('C', 'D')
diagram.edge('D', 'E')
diagram.edge('E', 'F')
diagram.edge('F', 'G')

# Render the diagram
diagram.render('OpenCLIP_Image_Recognition_Diagram', view=False)

# Creating a flowchart for OpenCLIP Image Recognition Process
flowchart = Digraph('OpenCLIPProcess', format='png')
flowchart.attr(rankdir='TB', size='8,5')

# Defining styles for different types of nodes
flowchart.attr('node', shape='circle', style='filled', color='orange', fontcolor='black')
flowchart.node('Start', 'Start')

flowchart.attr('node', shape='box', style='filled', color='lightcyan', fontcolor='black')
flowchart.node('LoadImage', 'Load Image from Path')
flowchart.node('ConvertRGB', 'Convert Image to RGB')
flowchart.node('TransformTensor', 'Apply Transform to Create Tensor')
flowchart.node('GenerateCaption', 'Generate Caption using OpenCLIP Model')
flowchart.node('OutputCaption', 'Output Descriptive Caption')

flowchart.attr('node', shape='circle', style='filled', color='orange', fontcolor='black')
flowchart.node('End', 'End')

# Defining edges between nodes
flowchart.edge('Start', 'LoadImage')
flowchart.edge('LoadImage', 'ConvertRGB')
flowchart.edge('ConvertRGB', 'TransformTensor')
flowchart.edge('TransformTensor', 'GenerateCaption')
flowchart.edge('GenerateCaption', 'OutputCaption')
flowchart.edge('OutputCaption', 'End')

# Render the flowchart
flowchart.render('OpenCLIP_Image_Recognition_Flowchart', view=False)

('OpenCLIP_Image_Recognition_Diagram.png', 'OpenCLIP_Image_Recognition_Flowchart.png')
