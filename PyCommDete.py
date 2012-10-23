#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import division
import networkx as nx
import matplotlib.pyplot as plt
from math import pow
from random import random

#import numpy, matplotlib
#from scipy.cluster import hierarchy
#from scipy.spatial import distance

f = file('./out', 'wa+')
C = nx.read_gml('./inputs/GML/polbooks.gml')
# C = nx.read_gml('./inputs/GML/karate.gml')
# C = nx.read_gml('./inputs/GML/dolphins.gml')

correct = float(-0.01)
alpha = 1.0
beta = 0.6
gama = 0.6


def get_maximum_cliques(network):
	# find the maximum cliques in network C, clique's nodes are over 2.
	# http://networkx.lanl.gov/reference/algorithms.clique.html
	cl = list(nx.find_cliques(network))
	cl_over_2 = [set(m) for m in cl if len(m) > 2]
#	print cl_over_2
	seeds = deal_cliques(cl_over_2)
	out_list = ["seeds", str(seeds), '\n']
	f.writelines(out_list)
	return seeds

def deal_cliques(cliques):
	# sort the list of lists based on the length of the list
	cliques.sort(key=lambda x:len(x), reverse=True)
	# merge the cliques if they are shared n-1 nodes
	result=[]
	le = len(cliques)
	if le == 0:
		return result
	elif le == 1:
		return list(cliques[0])

	current = cliques[0]
	current_len = len(current)
	i=1
	cliques_len = len(cliques)
	while i < cliques_len:
		if len(current.intersection(cliques[i])) == current_len-1:
			current = current.union(cliques[i])
		else:
			result.append(current)
			current = cliques[i]
			current_len = len(current)
		i = i+1
	result.append(current)
	result = list(result)
	result = [sorted(m) for m in result]
	result.sort(key=lambda x:len(x), reverse=True)
	print result
	return result

def get_neighbors(Graph):
	"""find subgraph's(or graph, type is Graph) neighbor nodes in original graph C"""
	#print "Graph:", Graph.nodes()
	#out_list = ["Graph:", str(Graph.nodes()),'\n']
	#f.writelines(out_list)
	G_neighbors = []
	t = []
	for x in Graph.nodes():
		t = C.neighbors(x)
		for y in t:
			if y not in Graph.nodes() and y not in G_neighbors:
				G_neighbors.append(y)
	#out_list = ["G_neighbors: ", str(G_neighbors), '\n']
	#f.writelines(out_list)
	#print "G_neighbors: ", G_neighbors
	return G_neighbors

def get_fitness(Graph):
	"""compute the fitness of the graph"""
	if len(Graph.nodes()) == 1:
		fitness_G = float(0)
	else:
		kin = 2 * len(Graph.edges())

		G_neighbors = get_neighbors(Graph)   # find G's neighbor nodes	
		G_with_neighbors = G_neighbors + Graph.nodes()
		G_nei = nx.Graph(C.subgraph(G_with_neighbors))	
		kout = len(G_nei.edges()) - len(Graph.edges())
		fitness_G = kin / pow((kin+kout), alpha)
	#print "fitness_G: ", fitness_G
	#out_list = ["fitness_G: ", str(fitness_G), '\n']
	#f.writelines(out_list)
	return fitness_G

def get_fitness_v_max(Graph):
	"""这有个问题，如果最大贡献度所对应的节点有多个怎么处理，是添加第一个最大的节点，还是所有的都添加
	compute the fitness_v(dic, {node, fitness of adding vertex}), find fitness_v_max"""
	G_neighbors = get_neighbors(Graph)
	#print "G_neighbors: ", G_neighbors
	fitness_v_max = float(-100)
	vertex = -1

	#vertex_list = []# 添加一个初始值    将最大贡献度所对应的一些节点一起加入社区
	if G_neighbors == []:
		pass
	else:
		fitness_v = {}
		G_nodes = Graph.nodes()
		#print "G_nodes: ", G_nodes
		for x in G_neighbors:
			#print "x: ", x
			G_nodes.append(x)
			Tmp = nx.Graph(C.subgraph(G_nodes))
			#print Tmp.nodes()
			fitness_v[x] = get_fitness(Tmp)
			G_nodes.pop(G_nodes.index(x))
		#print "fitness_v: ", fitness_v
		# find fitness_v_max		
		for x in fitness_v.keys():
			if fitness_v[x] > fitness_v_max:
				fitness_v_max = fitness_v[x]
				vertex = x
		#for x in fitness_v.keys():
		#	if fitness_v[x] == fitness_v_max:
		#		vertex_list.append(x)
	return (vertex, fitness_v_max)

def get_fitness_v_community(Graph):
	"""节点对社区的贡献度"""
	(vertex, fitness_v_max) = get_fitness_v_max(Graph)
	fitness_v_community	= fitness_v_max - get_fitness(Graph)
	#fitness_v_community += correct
	return (vertex, fitness_v_community)

def get_nature_community(Graph):	
	# form the new community G_iter, if fitness_v_max > 0
	(vertex, fitness_v_community) = get_fitness_v_community(Graph)
	#print "______", vertex, fitness_v_community
	G_nature_community = Graph

	if vertex == -1:
		return G_nature_community	

	#print "(vertex, fitness_v_community)", (vertex, fitness_v_community)
	out_list = ["(vertex, fitness_v_community)", str((vertex, fitness_v_community)), '\n']
	f.writelines(out_list)
	G_nodes = Graph.nodes()
	if fitness_v_community > 0: # 将节点对社区的贡献度大于0的节点加入社区.为什么不是0的时候这么慢？？？
		#G_nodes = G_nodes + vertex_list

		G_nodes.append(vertex)
		G_iter = nx.Graph(C.subgraph(G_nodes))
		out_list = [str(G_iter.nodes()), '\n']
		f.writelines(out_list)

		G_nature_community = get_nature_community(G_iter)
		#else:
		#	G_nature_community = G_iter

	#print "G_nature_community.nodes()", G_nature_community.nodes()
	#out_list = ["G_nature_community.nodes()", str(G_nature_community.nodes()), '\n']
	#f.writelines(out_list)

	return G_nature_community

def compare_communities(community1_nodes, community2_nodes):
	len1 = len(community1_nodes)
	len2 = len(community2_nodes)
	i = 0
	if len1 != len2:
		return 0

	while i < len1:
		if community1_nodes[i] != community2_nodes[i]:
			return 0
		i = i + 1
	return 1

def get_degree_max(nodes):
	degree_dict = C.degree()
	sub_degree_dict = {}
	for x in nodes:
		sub_degree_dict[x] = degree_dict[x]
	degrees = sub_degree_dict.values()
	#print "degrees", degrees
	degree_max = max(degrees)
	return  degrees.index(degree_max)

def get_all_nature_community(network):
	cliques = get_maximum_cliques(network)
	i = 0
	communities = []
	tem_list1 = []
	left_list = []
	communities_end = []
	single_node_Graph = nx.Graph()
	while i < len(cliques):
		out_list = ['clique:', str(cliques[i]), '\n']
		f.writelines(str(cliques[i]))
		Graph = nx.Graph(network.subgraph(cliques[i]))
		communities.append(get_nature_community(Graph))
		#print "i = ", i
		#print communities[i].nodes()
		out_list = ["i = ", str(i), str(communities[i].nodes()), '\n']
		f.writelines(out_list)
		for x in communities[i].nodes():
			if x not in tem_list1:
				tem_list1.append(x)
		i = i+1

	# incase there are some isolated nodes
	i = i-1

	for x in network.nodes():
		if x not in tem_list1:
			left_list.append(x)
	#print "left_list",left_list
	if left_list != []:
		seed_node = get_degree_max(left_list)
		#print "seed_node",seed_node
		single_node_Graph.add_node(seed_node)
		communities.append(get_nature_community(single_node_Graph))
		for m in get_nature_community(single_node_Graph).nodes():
			if m not in tem_list1:
				tem_list1.append(m)
	communities = deal_communities(communities)

	return communities

def deal_communities(communities):
	# if there are some communities are the same, than delete
	for x in communities:
		for y in communities[communities.index(x)+1:]:
			com = compare_communities(x.nodes(), y.nodes())
			if com == 1:
				communities.pop(communities.index(y))
	f.writelines("++++++++++++++++++++++\n")
	out_list = [str(x.nodes()) for x in communities]
	f.writelines(out_list)
	f.writelines("eeeeeeeeeeeeeeeeeeeeee\n")
	# for debugging
	for x in communities:
		if len(x.nodes()) == len(C.nodes()):
			communities.pop(communities.index(x))

	# is_sub_graph
	def to_be_del(item, com):
		for x in com:
			if len(x)<= len(item):
				continue
			else:
				if set(item).issubset(set(x.nodes())):
					return True
		return False
	bitmap=[0]*len(communities)
	for i in range(len(communities)):
		if to_be_del(communities[i].nodes(), communities):
			bitmap[i]=1
	for i in range(len(bitmap)-1, -1, -1):
		if bitmap[i]:
			communities.pop(i)
	return communities

def get_overlapping_nodes(community1_nodes, community2_nodes):
	overlapping_nodes = []
	for x in community1_nodes:
		if x in community2_nodes:
			overlapping_nodes.append(x)
	return overlapping_nodes

def get_merging_nodes(community1_nodes, community2_nodes):
	merging_nodes = community1_nodes
	for x in community2_nodes:
		if x not in merging_nodes:
			merging_nodes.append(x)
	return merging_nodes

def get_communities_overlapping_degree(community1, community2):

	nei1 = get_neighbors(community1)
	nei2 = get_neighbors(community2)
	if len(get_merging_nodes(nei1, nei2)) == 0:
		COD = len(get_overlapping_nodes(community1.nodes(), community2.nodes())) \
	/ len(get_merging_nodes(community1.nodes(), community2.nodes()))
	else:
		COD = beta*len(get_overlapping_nodes(community1.nodes(), community2.nodes())) \
	/ len(get_merging_nodes(community1.nodes(), community2.nodes())) + (1-beta) \
	* len(get_overlapping_nodes(nei1, nei2)) / len(get_merging_nodes(nei1, nei2))
	return COD

def merge_communities(community1, community2):
	community_new = nx.Graph(C.subgraph((community1.nodes() + community2.nodes())))
	#print "merge:",community_new.nodes()
	out_list = ["merge:",str(community_new.nodes()),'\n']
	f.writelines(out_list)
	#f.write("merge----------------------\n")
	return community_new

def get_all_COD(communities):
	#计算社区中两两社区的社区重叠度,,未用
	COD = []
	for x in communities:
		for y in communities[(communities.index(x)+1):]:
			#print communities.index(x), x.nodes()
			#print communities.index(y), y.nodes()
			cod = get_communities_overlapping_degree(x, y)
			COD.append([cod, x, y])
	return COD

def is_sub_graph(graph1, graph2):
	len1 = len(graph1.nodes())
	len2 = len(graph2.nodes())
	set1 = set(graph1.nodes())
	set2 = set(graph2.nodes())
	min_graph = nx.Graph()
	if len1 >= len2:
		if set2.issubset(set1) == True:
			min_graph = graph2
		return (set2.issubset(set1), min_graph)
	else:
		if set1.issubset(set2) == True:
			min_graph = graph1
		return (set1.issubset(set2), min_graph)

def merge_all_communities(communities):####TODO  pop y可以,pop x会多pop出去  我觉得应该把cod的判断放在外边

	# 遍历一遍
	communities_end = []
	communities_iter = communities
	flag = -1
	for x in communities_iter:
		for y in communities_iter[communities_iter.index(x)+1:]:
			#print communities_iter.index(x), x.nodes()
			out_list = [str(communities_iter.index(x)), str(x.nodes()), '\n']
			f.writelines(out_list)
			#print communities_iter.index(y), y.nodes()
			out_list = [str(communities_iter.index(y)), str(y.nodes()), '\n']
			f.writelines(out_list)
			cod = get_communities_overlapping_degree(x, y)
			#print "cod:", cod
			out_list = ["cod:", str(cod)]
			f.writelines(out_list)
			if cod > gama:
				#COD.append([cod, x, y])
				merge_graph = merge_communities(x, y)
				if merge_graph.nodes() == x.nodes():
					f.write("!c_end!end!!!!!!!!!!!!!!!!!!!!\n")
					communities_iter.pop(communities_iter.index(y))
					f.write("pop communities  y   !!!!!!!!!!!!!\n")
					out_list = [str(x.nodes()) for x in communities_iter]
					f.writelines(out_list)
					f.write("!c_end!end!!!!!!!!!!!!!!!!!!!!\n")
					flag = -1
					break
				elif merge_graph.nodes() == y.nodes():
					flag = 1
					break
				else:
					communities_iter.append(merge_graph)
					#print "merge: ", merge_communities(x, y)
					#f.write("merge-------------------")
					f.write("add merged communities!!!!!!!!!!!!!\n")
					out_list = [str(x.nodes()) for x in communities_iter]
					f.writelines(out_list)
					f.write("!c_end!end!!!!!!!!!!!!!!!!!!!!\n")
					communities_iter.pop(communities_iter.index(y))
					f.write("pop communities  y   !!!!!!!!!!!!!\n")
					out_list = [str(x.nodes()) for x in communities_iter]
					f.writelines(out_list)
					f.write("!c_end!end!!!!!!!!!!!!!!!!!!!!\n")
					flag = 1
					break
		if flag == 1:
			communities_iter.pop(communities_iter.index(x))
			f.write("pop communities  x   !!!!!!!!!!!!!\n")
			out_list = [str(x.nodes()) for x in communities_iter]
			f.writelines(out_list)
			f.write("!c_end!end!!!!!!!!!!!!!!!!!!!!\n")
			flag = -1			
			if communities_end != communities_iter:
				communities_end = merge_all_communities(communities_iter)

	communities_end = communities_iter

	#print "~~~~~~~~~~~~"
	#for m in communities_end:
	#	print m.nodes()
	f.write("!!!!!!!!!!!!!final\n")
	out_list = [str(x.nodes()) for x in communities_end]
	f.writelines(out_list)
	f.write("!c_end!end\n")
	return communities_end


def main():
	# read network dataset as graph C

	#nx.draw(C)
	#plt.savefig("karate_club_graph.png")
	#print C.nodes()
	#print C.edges()

	# init
	# communities = []


	communities = get_all_nature_community(C)
	#i = 0
	#while i < len(communities):
	#	print "i = ", i
	#	print communities[i].nodes()
	#	i = i+1
	f.write("++++++++++++++++++++++++++++++\n")
	out_list = [str(communities[i].nodes()) for i in range(len(communities))]
	f.writelines(out_list)
	f.write("++++++++++++++++++++++++++++++end\n")

	# 合并		
	results = merge_all_communities(communities)
	position = nx.circular_layout(C)

	f.write("----------------------------------The detection result is: \n")
	out_list = [str(sorted(results[i].nodes())) for i in range(len(results))]
	f.writelines(out_list)
	f.write("----------------------------------end\n")


	overlapping_nodes = set([])
	f.write("overlapping nodes are: ------------\n")
	communities = [set(x) for x in communities]
	for x in communities:
		for y in communities[communities.index(x)+1:]:
			temp = x.intersection(y)
			overlapping_nodes = overlapping_nodes.union(temp)
	f.writelines(str(list(overlapping_nodes)))
	f.write("----------------------------------end\n")						
	f.close()


	for x in results:
		nx.draw(x, node_color = (random(), random(), random()))
	#nx.draw(nx.Graph(C.subgraph(overlapping_nodes)), node_color = "r")
	plt.savefig("CD_output.png")

if __name__ == '__main__':
	main()
	#import profile
	#profile.run("main()")
	#import pstats
	#p = pstats.Stats('./pro_out')
	#p.sort_stats("time").print_stats()
