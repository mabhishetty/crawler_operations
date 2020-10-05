# 4/10/20
# Edition 3
# Module to convert my output from the Crawler program - a crawler object - to a NetworkX graph.
# This NetworkX graph can then be drawn with NetworkX methods or with (Py)Graphviz.
# New additions: attempts to manage numbering, adding key, don't default any shapes
# set attribute of node to show which node it comes from

def crawler2networkx(crawler):
    # 1. Import necessary modules. Set up important numbers
    import matplotlib.pyplot as plt                # I think this is because networkx is built upon matplotlib
    import networkx as nx
    import math
    import numpy as np
    from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
    import pygraphviz as pgv
    from sys import exit

    # 2. Now we need to perform some operations on the crawler data.
    # We aren't able to modify Graphviz attributes once the graph is drawn. I cannot find a way to access the Graphviz attributes once added.
    # (https://stackoverflow.com/questions/44337180/graphviz-python-recoloring-a-single-node-after-it-has-been-generated)
    # So I will get all the necessary information first, then construct the nodes.
    # Empty storage
    graph_dict = {}
    listOfLists = []
    # 2.1. Assemble a dictionary that, for each site_visited, gives the unique links on that site and their multiplicity.
    for i in range(1, len(crawler.sites_visited) + 1):
        # empty list which will store the repeat links from this particular site_visited
        listForRepeats = []
        graph_dict[i] = {}
        a = 1
        for x in range(1, len(crawler.sites_dict.get(i).get('links')) + 1):
            y = (crawler.sites_dict.get(i).get('links'))[x - 1]
            # If we already have a link for this site
            if y in listForRepeats:
                continue
            else:
                # Add it to the dictionary, along with a count of how many times it appears
                graph_dict.get(i).update({a: [y, crawler.sites_dict.get(i).get('links').count(y)]})
                listForRepeats.append(y)
                a += 1
        listOfLists.append(listForRepeats)
    # 2.2. Now we have a dictionary in this form: {1:{1:[link, num]}
                                            #    2:[link, num]}
    # And a list of lists of all the links.
    # 2.3.From stackoverflow (https://stackoverflow.com/questions/2116286/python-find-identical-items-in-multiple-lists), we use a function to find repeats between lists:
    seen = set()                                        # An unordered, unindexed collection with no repeats
    repeated = set()
    for l in listOfLists:
        for ff in set(l):
            if ff in crawler.sites_visited:             # Small amendment to this - I do not want to include any of the sites_visited here.
                continue
            elif ff in seen:
                repeated.add(ff)
            else:
                seen.add(ff)
    # Now 'repeated' contains a set of elements that are repeated links among all - bar the sites_visited. This is because I don't want the sites_visited to be redrawn.

    # 3. From matplotlib, we say colours have six-digit hex values. Don't want to use white though, so will restrict the range from ffffff to 777777
    maxColourIndex = int('777777', 16)
    # 4. Get the number of sites visited in total
    numSites = len(crawler.sites_visited)
    # 5. Set up colours
    # 5.1. We will use this to scale up colours, so they are far apart. Subtract 1 because we include 0.
    multiplierToScale = math.floor(maxColourIndex/(numSites - 1))
    # 5.2. Array of consecutive integers up to 1 below the number of sites (1 below since we include 0)
    numSitesArray = range(0,numSites)
    # 5.3. Numbers are now spread equally over our range - to cover all possible colours in the range.
    coloursDecimal = np.multiply(numSitesArray, multiplierToScale)
    # 6. (Loop Start)
    # Create empty directed graph.
    G = nx.DiGraph()
    # 6. In a loop over the sites visited, add the sites_visited nodes to the graph:
    # 6.1. Storage of nodes:
    nodeStorage = []
    for visIndex in range(1, numSites + 1):
        # get colour for this site_visited in hex.
        hex_colour = '#{:06x}'.format(coloursDecimal[visIndex-1])
        # If our colour is black, write in white text (so we can see it.)
        if hex_colour == '#000000':
            writeColor = 'white'
        else:
            writeColor = 'black'
        # This should really never happen because of the checks in crawler_f1.py. Including just in case.
        if crawler.sites_dict.get(visIndex).get('url') in nodeStorage:
            exit("A site in the visited_sites has been repeated. That shouldn't have happened!")
        else:
            # Add these nodes to the graph and then to the list of nodes not to add again
            G.add_node(crawler.sites_dict.get(visIndex).get('url'), style = 'filled', fillcolor = hex_colour, label = str(visIndex), tooltip = crawler.sites_dict.get(visIndex).get('url'), shape = 'box', fontcolor = writeColor)
            nodeStorage.append(crawler.sites_dict.get(visIndex).get('url'))


    # 7. Now we go over the rest of the nodes.
    # KEY: FillColor - white: a node with links from more than one of the sites_visited
                    #- else: colour corresponds to the site_visited which held that link
         # Shape - circle: standard link
                #- triangle: 'None' link
                #- diamond: Link starts with a '#' (linking content on same page)
    # We add weights and use those values as edge tooltips too.
    # node tooltips are urls.
    # For each node, add: ID (how you identify node) style (filled in), color, tooltip (message when you hover), label (what is displayed on the node), fontcolor and shape
    # For each edge, add: from node, to node (first two args), tooltip (when hovering), weight, color
    for r in range(1, numSites + 1):
        hex_colour = '#{:06x}'.format(coloursDecimal[r-1])
        # 7.1. If the colour of the node is black, set the text to be white so that we can read it.
        if hex_colour == '#000000':
            writeColor = 'white'
        else:
            writeColor = 'black'
        # 7.2. For each visited site, go over all of the links.
        a = 1

        for iterator in range(1, len(graph_dict.get(r)) + 1):
            # 7.3. List of form [link, multiplicity]
            linkyList = graph_dict.get(r).get(iterator)
            # 7.4. get link
            linkHere = linkyList[0]
            # 7.5. If we already have a node for this link, add an edge BUT NOT another node. Edge from the current site_visited we are on to this link
            if linkHere in nodeStorage:
                if linkHere is None:
                    G.add_edge(crawler.sites_dict.get(r).get('url'), 'None', tooltip = linkyList[1], weight = linkyList[1], color = hex_colour)
                else:
                    G.add_edge(crawler.sites_dict.get(r).get('url'), linkHere, tooltip = linkyList[1], weight = linkyList[1], color = hex_colour)
                nodeStorage.append(linkHere)
            # 7.6. If we don't already have a node, but this node will be repeated - add the node but in the colour white.
            elif linkHere in repeated:
                if linkHere is None:
                    # Special case as None needs to be written as a string. (triangle)
                    G.add_node('None', style = 'filled', fillcolor = 'white', tooltip = linkHere, label = str(r) + '.' + str(a), fontcolor = 'black', shape = 'triangle')
                    G.add_edge(crawler.sites_dict.get(r).get('url'), 'None', tooltip = linkyList[1], weight = linkyList[1], color = hex_colour)
                elif linkHere.startswith('#'):
                    # special case - diamond shape
                    G.add_node(linkHere, style = 'filled', fillcolor = 'white', tooltip = linkHere, label = str(r) + '.' + str(a), fontcolor = 'black', shape = 'diamond')
                    G.add_edge(crawler.sites_dict.get(r).get('url'), linkHere, tooltip = linkyList[1], weight = linkyList[1], color = hex_colour)
                else:
                    G.add_node(linkHere, style = 'filled', fillcolor = 'white', tooltip = linkHere, label = str(r) + '.' + str(a), fontcolor = 'black', shape = 'circle')
                    G.add_edge(crawler.sites_dict.get(r).get('url'), linkHere, tooltip = linkyList[1], weight = linkyList[1], color = hex_colour)
                a += 1
                nodeStorage.append(linkHere)
            # 7.7. if we don't have a node already and it is not repeated - this link is unique to this site_visited. All that is different from above is the fillcolor - which now matches the site_visited.
            else:
                if linkHere is None:
                    G.add_node('None', style = 'filled', fillcolor = hex_colour, tooltip = linkHere, label = str(r) + '.' + str(a), fontcolor = writeColor, shape = 'triangle')
                    G.add_edge(crawler.sites_dict.get(r).get('url'), 'None', tooltip = linkyList[1], weight = linkyList[1], color = hex_colour)
                elif linkHere.startswith('#'):
                    G.add_node(linkHere, style = 'filled', fillcolor = hex_colour, tooltip = linkHere, label = str(r) + '.' + str(a), fontcolor = writeColor, shape = 'diamond')
                    G.add_edge(crawler.sites_dict.get(r).get('url'), linkHere, tooltip = linkyList[1], weight = linkyList[1], color = hex_colour)
                else:
                    G.add_node(linkHere, style = 'filled', fillcolor = hex_colour, tooltip = linkHere, label = str(r) + '.' + str(a), fontcolor = writeColor, shape = 'circle')
                    G.add_edge(crawler.sites_dict.get(r).get('url'), linkHere, tooltip = linkyList[1], weight = linkyList[1], color = hex_colour)
                a += 1
                nodeStorage.append(linkHere)
                # 7.8. setting a default.
    strTitle = 'Title: Network representation of the web: starting from {} and visiting {} sites (known as \'sitesVisited\').'.format(crawler.sites_visited[0], len(crawler.sites_visited))
    str1 = 'Node legend:\n\tWhite: Nodes that may be reached from more than one of the sitesVisited.'
    str2 = 'Circle: standard node.'
    str3 = 'Diamond: link starts with \'#\' -- to content on the same siteVisited.'
    str4 = 'Triangle: link is title \'None\'.'
    G.graph['edges']={'arrowsize':'4.0'}
    # Graph title
    G.graph['label'] = strTitle + '\n' + str1 + '\n\t' + str2 +'\n\t' + str3 + '\n\t' + str4
    # put label to top
    G.graph['labelloc'] = "t"
    # justification/alignment of label
    G.graph['nojustify'] = "true"
    # 8. This now makes our graphviz object
    A = to_agraph(G)
    #print(A)
    A.layout('dot')
    # the filename for the graph - in scalable vector graphics format (supports tooltips.)
    A.draw('myGraph.svg')
