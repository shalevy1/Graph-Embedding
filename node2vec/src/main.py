"""
Reference implementation of node2vec.

Author: Aditya Grover

For more details, refer to the paper:
node2vec: Scalable Feature Learning for Networks
Aditya Grover and Jure Leskovec
Knowledge Discovery and Data Mining (KDD), 2016
"""

import argparse
import networkx as nx
import node2vec
import classify
from gensim.models import Word2Vec



def parse_args(p,q):
    parser = argparse.ArgumentParser(description="Run node2vec.")

    # parser.add_argument('--input', nargs='?', default='../graph/karate.edgelist',
    #                     help='Input graph path')
    # parser.add_argument('--output', nargs='?', default='../emb/karate.emb',
    #                     help='Embeddings path')

    parser.add_argument('--input', nargs='?', default='../../data/BlogCatalog-dataset/data/edges.txt',
                        help='Input graph path')
    parser.add_argument('--output', nargs='?', default='../../data/BlogCatalog-dataset/data/blog_'+str(p)+'_'+str(q)+'.emb', help='Embeddings path')

    parser.add_argument('--groups', nargs='?', default='../../data/BlogCatalog-dataset/data/group-edges.txt',
                        help='Input graph path')

    parser.add_argument('--dimensions', type=int, default=128,
                        help='Number of dimensions. Default is 128.')

    parser.add_argument('--walk-length', type=int, default=80,
                        help='Length of walk per source. Default is 80.')

    parser.add_argument('--num-walks', type=int, default=10,
                        help='Number of walks per source. Default is 10.')

    parser.add_argument('--window-size', type=int, default=10,
                        help='Context size for optimization. Default is 10.')

    parser.add_argument('--iter', default=10, type=int,
                        help='Number of epochs in SGD')

    parser.add_argument('--workers', type=int, default=8,
                        help='Number of parallel workers. Default is 8.')

    parser.add_argument('--p', type=float, default=p,
                        help='Return hyperparameter. Default is 1.')

    parser.add_argument('--q', type=float, default=q,   # similar with BFS style strategy.
                        help='Inout hyperparameter. Default is 1.')

    parser.add_argument('--delimiter', type=str, default=',',
                        help='the delimiter of a graph. Default is ",".')

    parser.add_argument('--weighted', dest='weighted', action='store_true',
                        help='Boolean specifying (un)weighted. Default is unweighted.')
    parser.add_argument('--unweighted', dest='unweighted', action='store_false')
    parser.set_defaults(weighted=False)

    parser.add_argument('--directed', dest='directed', action='store_true',
                        help='Graph is (un)directed. Default is undirected.')
    parser.add_argument('--undirected', dest='undirected', action='store_false')
    parser.set_defaults(directed=False)
    # parser.set_defaults(directed=True)

    return parser.parse_args()


def read_graph():
    """
	Reads the input network in networkx.
	"""
    if args.weighted:
        G = nx.read_edgelist(args.input, nodetype=int, data=(('weight', float),), create_using=nx.DiGraph(), delimiter=args.delimiter)
    else:
        G = nx.read_edgelist(args.input, nodetype=int, create_using=nx.DiGraph(), delimiter=args.delimiter)
        for edge in G.edges():
            G[edge[0]][edge[1]]['weight'] = 1
    if not args.directed:
        G = G.to_undirected()

    return G


def learn_embeddings(walks):
    """
	Learn embeddings by optimizing the Skip-gram objective using SGD.
	"""
    walks = [list(map(str, walk)) for walk in walks]
    model = Word2Vec(walks, size=args.dimensions, window=args.window_size, min_count=0, sg=1, workers=args.workers, iter=args.iter)
    model.wv.save_word2vec_format(args.output)
    print("Save.")

    return model


def main(args):
    """
	Pipeline for representational learning for all nodes in a graph.
	"""
    nx_G = read_graph()  # 利用networkx包读取Graph信息
    G = node2vec.Graph(nx_G, args.directed, args.p, args.q)  # 使用node2vec中的公式进行一下处理
    G.preprocess_transition_probs()  # 计算新的概率
    # 这里计算完毕，是返回一系列walks的路径，这些路径中允许出现重复点，例如：0->1->5->4->7->1->4 等
    walks = G.simulate_walks(args.num_walks, args.walk_length)
    model = learn_embeddings(walks)
    return model


if __name__ == "__main__":
    """
    ps = [0.25, 0.5, 1.0, 2.0, 4.0]
    qs = [0.25, 0.5, 1.0, 2.0, 4.0]
    for p in ps:
        for q in qs:
    """
    p = q = 0.25
    args = parse_args(p,q)
    # model = main(args)
    # classify.classification(args)
    classify.scoring(args)


