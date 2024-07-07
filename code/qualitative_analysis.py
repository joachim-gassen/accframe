import logging
import numpy as np
import pandas as pd
import psutil
import requests
import subprocess
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import time

logging.basicConfig(level=logging.INFO)

local_llm_cfg = {
    "path_to_compiled_llama_server_executable": "../botex/llama.cpp/server",
    "local_model_path": "../botex/models/Mistral-7B-Instruct-v0.3.Q4_K_M.gguf",
    "num_layers_to_offload_to_gpu": 99,
}

EXPERIMENT = [
    {
        "data": "data/generated/honesty_2024-06-17_rounds.csv", 
        "vars": ["reported_amount_reason"],
        "experiments": ["honesty", "fhonesty"],
        "statements": [
            "I chose tp report my points to ensure that the other person also gets a fair payoff.", 
            "I chose to maximize my payoff.", 
            "I chose to report the honest and true amount."
        ],
    },
    {
        "data": "data/generated/trust_2024-06-18_rounds.csv",
        "vars": ["sent_reason", "sent_back_reason"],
        "statements": [
            "I care about other people", 
            "I want to maximize my payoff", 
            "I trust the other person", 
            "I want to to be fair"
        ]
    },
    {
        "data": "data/generated/giftex_2024-06-18_rounds.csv",
        "vars": ["wage_reason", "effort_reason"],
        "statements": [
            "I care about other people", 
            "I want to maximize my payoff", 
            "I trust the other person", 
            "I want to to be fair"
        ]
    },
]

NUM_CLUSTERS = 3


def main():
    for exp in EXPERIMENT:
        df = pd.read_csv(exp["data"], na_values=["", " ", "NA", "N/A", "null"])
        llama_server = start_llama_cpp_server(**local_llm_cfg)
        # get embeddings based on the vars in the experiment
        for var in exp["vars"]:
            embeddings = get_local_llm_embedding(df[var], var)
            df[var + "_embeddings"] = embeddings
            centroids = get_local_llm_embedding_statements(exp["statements"])
            df = compute_cluster_centroid_similarity_score(df, centroids, var)
            df.to_csv(f"{exp['data'][:-4]}_with_statement_sim.csv", index=False)
            representative_texts = cluster_embeddings(df, var)
            representative_texts.to_csv(
                f"{exp['data'][:-4]}_{var}_representative_texts.csv", index=False
            )
        stop_llama_cpp_server(llama_server)


def start_llama_cpp_server(
    path_to_compiled_llama_server_executable,
    local_model_path,
    num_layers_to_offload_to_gpu,
):
    cmd = [
        str(path_to_compiled_llama_server_executable),
        "-m",
        str(local_model_path),
        "--embeddings",
        "-c",
        "4096",
        "-ngl",
        str(num_layers_to_offload_to_gpu),
    ]

    logging.info(f"Starting llama server")

    with open("llama_cpp_server.log", "a") as log_file:
        process = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.PIPE)

    if wait_for_server():
        logging.info("LLM server started successfully.")
        return process
    else:
        logging.error("Failed to start the LLM server.")
        raise Exception("Failed to start the LLM server.")


def wait_for_server(timeout=10):
    """
    Waits for the server to become responsive.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:8080/health")
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            time.sleep(1)
    return False


def stop_llama_cpp_server(process: subprocess.Popen):
    """
    Stops the local language model server.
    """
    if process:
        logging.info("Stopping server...")
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()

        process.wait()
        logging.info("Server stopped.")
    else:
        logging.warning("Server is not running.")

def get_local_llm_embedding_statements(statements):

    url = "http://localhost:8080/v1/embeddings"

    payloads = {"input": statements, "encoding_format": "float"}
    response = requests.post(url, json=payloads)

    if response.status_code == 200:
        embeddings = [e["embedding"] for e in response.json()["data"]]
        return embeddings
    else:
        raise Exception("Failed to get embeddings from local LLM")

def get_local_llm_embedding(texts, var):

    url = "http://localhost:8080/v1/embeddings"

    texts = texts.reset_index()
    no_missing = texts.copy().dropna()
    no_missing_texts = no_missing[var].tolist()
    payloads = {"input": no_missing_texts, "encoding_format": "float"}
    response = requests.post(url, json=payloads)

    if response.status_code == 200:
        embeddings = [e["embedding"] for e in response.json()["data"]]
        no_missing["embeddings"] = embeddings
        texts = pd.merge(texts, no_missing, on="index", how="left")
        return texts["embeddings"]
    else:
        raise Exception("Failed to get embeddings from local LLM")


def cluster_embeddings(df, var, n_clusters=NUM_CLUSTERS):
    df = df.reset_index()
    no_missing = df.copy().dropna()
    embeddings = np.array(no_missing[var + "_embeddings"].tolist())

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(embeddings)
    centroids = kmeans.cluster_centers_

    closest, _ = pairwise_distances_argmin_min(centroids, embeddings)
    representative_texts = pd.DataFrame(
        {
            f"{var}_cluster": range(n_clusters), 
            f"{var}_representative_text": no_missing.iloc[closest][var],
        }
    )
    return representative_texts


import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def compute_cluster_centroid_similarity_score(df, centroids, var):
    df[var + "_embeddings"] = df[var + "_embeddings"].apply(np.array)

    for i, centroid in enumerate(centroids):
        centroid = np.array(centroid)
        df[f"{var}_similarity_score_statement_{i + 1}"] = df[var + "_embeddings"].apply(
            lambda x: cosine_similarity(x.reshape(1, -1), centroid.reshape(1, -1))[0][0]
        )
    return df


if __name__ == "__main__":
    main()