from collections import defaultdict
import math
from functools import reduce
import psycopg2
import psycopg2.extras
import networkx as nx




hostname = 'localhost'
database = 'Db_pstdigital'
username = 'postgres'
pwd = 'Fathur27!!..))'
port = '5432'

conn = psycopg2.connect(dbname = database, user = username, 
                        password = pwd, host = hostname, port = port)
cursor = conn.cursor()

n = 0  # ukuran korpus
dictionary = set()  # dictionary untuk memuat semua istilah dalam dokumen
postings = defaultdict(dict)  # frekuensi kemunculan istilah
frekuensi_dokumen = defaultdict(int)
length = defaultdict(float)
characters = " .,-!#$%^&*();:\n\t\\\"?!{}[]<>"  # karakter yang akan dihapus dalam dokumen

def main(cursor):
    inisialisasi_dokumen(cursor)
    inisialisasi_frekuensi_dokumen()
    inisialisasi_lengths()

def inisialisasi_dokumen(cursor):
    global n, dictionary, postings
    cursor.execute("SELECT id_buku, judul, abstrak FROM publikasi")
    rows = cursor.fetchall()
    n = len(rows)
    for row in rows:
        id = row[0]
        judul = row[1]
        abstrak = row[2]
        istilah = tokenisasi(f"{judul} {abstrak}")
        istilah_unik = set(istilah)
        dictionary = dictionary.union(istilah_unik)
        for term in istilah_unik:
            postings[term][id] = istilah.count(term)

def tokenisasi(database:str):
    istilah = database.lower().split()
    return [term.strip(characters) for term in istilah]

def inisialisasi_frekuensi_dokumen():
    global frekuensi_dokumen
    for term in dictionary:
        frekuensi_dokumen[term] = len(postings[term])

def inisialisasi_lengths():
    global length
    for id in range(1, 1):
        l = 0
        for term in dictionary:
            l += tfidf(term, id)
        if l != 0:  # Periksa apakah panjang dokumen (l) tidak nol sebelum menghitung akar kuadrat
            length[id] = math.sqrt(l)**2
        else:
            length[id] = 1  # Atau beri nilai default jika panjang dokumen adalah nol

def calc_TF(document:dict):
    TF_dict = {}
    for term in document:
        if term in TF_dict:
            TF_dict[term] += 1
        else:
            TF_dict[term] = 1

    # Computes tf for each word
    for term in TF_dict:
        TF_dict[term] = TF_dict[term] / len(document)

    return TF_dict

def tf(term:str, document:dict):
    TF_dict = calc_TF(document)
    return TF_dict.get(term, 0)

def tfidf(term, id):
    if id in postings[term]:
        return tf(term, get_document_terms(id)) * inverse_frekuensi_dokumen(term)
    else:
        return 1

def inverse_frekuensi_dokumen(term):
    if term in dictionary:
        return math.log(n/frekuensi_dokumen[term] + 1)

def intersection(sets):
    return reduce(set.intersection, [s for s in sets])

def weighted_tree_similarity(query, id:int):
    G_query = construct_weighted_tree(query)
    G_document = construct_weighted_tree(get_document_terms(id))

    # Calculate Jaccard Similarity between the weighted trees
    intersection_size = len(set(G_query.nodes) & set(G_document.nodes))
    union_size = len(set(G_query.nodes) | set(G_document.nodes))

    if union_size != 0:
        jaccard_similarity = intersection_size / union_size
    else:
        jaccard_similarity = 0.0

    return jaccard_similarity

def construct_weighted_tree(terms):
    G = nx.Graph()
    G.add_nodes_from(terms)

    for i in range(len(terms) - 1):
        for j in range(i + 1, len(terms)):
            edge_weight = weighted_edge(terms[i], terms[j])
            if edge_weight > 0:
                G.add_edge(terms[i], terms[j], weight=edge_weight)
    return G

def weighted_edge(term1, term2):
    if term1 in dictionary and term2 in dictionary:
        return inverse_frekuensi_dokumen(term1) + inverse_frekuensi_dokumen(term2)
    else:
        return 0.0

def get_document_terms(id:int):
    cursor.execute("SELECT judul, abstrak FROM publikasi WHERE id_buku = %s", (id,))
    row = cursor.fetchone()
    document_text = f"{row[0]} {row[1]}"
    return tokenisasi(document_text)

def similarity(query, id):
    tfidf_similarity = 0.5 * sum(tfidf(term, id) for term in query)
    tree_similarity = 0.5 * weighted_tree_similarity(query, id)

    # Check if length[id] is not zero before division
    if length[id] != 0:
        tfidf_similarity /= length[id]
    else:
        print(tfidf_similarity + tree_similarity)

    return tfidf_similarity + tree_similarity