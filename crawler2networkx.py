# 3/10/20
# Edition 2
# Module to convert my output from the Crawler program - a crawler object - to a NetworkX graph.
# This NetworkX graph can then be drawn with NetworkX methods or with Cytoscape (accessed in Python through CyREST)

def crawler2networkx(crawler):
    # 1. Import necessary modules. Set up important numbers
    import matplotlib.pyplot as plt                # I think this is because networkx is built upon matplotlib
    import networkx as nx
    import math
    import numpy as np
    from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
    import pygraphviz as pgv

    # 2. From matplotlib, we say colours have six-digit hex values.
    maxColourIndex = int('ffffff', 16)
    # 3. Get the number of sites visited in total
    numSites = len(crawler.sites_visited)
    # 3. Set up colours
    # 3.1. We will use this to scale up colours, so they are far apart. Subtract 1 because we include 0.
    multiplierToScale = math.floor(maxColourIndex/(numSites - 1))
    # 3.2. Array of consecutive integers up to 1 below the number of sites (1 below since we include 0)
    numSitesArray = range(0,numSites)
    # 3.3. Numbers are now spread equally over our range - to cover all possible colours in the range.
    coloursDecimal = np.multiply(numSitesArray, multiplierToScale)
    # 4. (Loop Start)
    # Create empty directed graph.
    G = nx.DiGraph()
    # 5. Loop over the number of sites that we visited.
    for i in range (1,len(crawler.sites_visited) + 1):
        # 5.1. Get the colour for this site. Take an element from our list and write in 6-digit hex.
        hex_colour = '#{:06x}'.format(coloursDecimal[i-1])
        # 5.2. If the colour of the node is black, set the text to be white so that we can read it.
        if hex_colour == '#000000':
            writeColor = 'white'
        else:
            writeColor = 'black'
        # 5.3. Add a node for the site that we visited. Our node ID is the url of this site. We fill the node with our colour, give a special shape and font colour. Set text to be the iteration number and hover to get URL.
        G.add_node(crawler.sites_dict.get(i).get('url'), tooltip = crawler.sites_dict.get(i).get('url'), style = 'filled',  fillcolor = hex_colour, label = str(i), shape = 'box', fontcolor = writeColor)
        # 5.4. Loop over all the links from this site and draw those nodes and edges (different shape)
        for ii in range(1, len(crawler.sites_dict.get(i).get('links')) + 1):
            # 5.4.1. Our link to visit is from the dictionary.
            secondaryLink = list(crawler.sites_dict.get(i).get('links'))[ii-1]
            if secondaryLink is None:
                G.add_node('None', tooltip = 'None', style = 'filled', fillcolor = hex_colour, label = str(i) + '.' + str(ii), shape = 'triangle', fontcolor = writeColor)
                G.add_edge(crawler.sites_dict.get(i).get('url'), 'None')
            elif secondaryLink.startswith('#'):
                G.add_node(secondaryLink, tooltip = secondaryLink, style = 'filled', fillcolor = hex_colour, label = str(i) + '.' + str(ii), shape = 'diamond', fontcolor = writeColor)
                G.add_edge(crawler.sites_dict.get(i).get('url'), secondaryLink)
            else:
                G.add_node(secondaryLink, tooltip = secondaryLink, style = 'filled', fillcolor = hex_colour, label = str(i) + '.' + str(ii), fontcolor = writeColor)
                G.add_edge(crawler.sites_dict.get(i).get('url'), secondaryLink)

        G.graph['node']={'shape':'circle'}
        G.graph['edges']={'arrowsize':'4.0'}

        A = to_agraph(G)
        #print(A)
        A.layout('dot')
        A.draw('abcde.svg')

        # ?? Need to figure out a way to know when the links from one site have finished and another begins
