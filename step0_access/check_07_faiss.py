"""C4 -- faiss-cpu: flat inner-product index and IndexIVFPQ over 1M x 256 float32."""
import json, os, time

import numpy as np

from _common import jdump

N = 1_000_000
D = 256
NQ = 1_000
K = 32


def rss_gb():
    import resource
    # ru_maxrss is bytes on macOS, kilobytes on Linux
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


def main():
    import faiss

    res = {"faiss_version": faiss.__version__, "n": N, "d": D, "nq": NQ, "k": K,
           "threads": faiss.omp_get_max_threads()}

    rng = np.random.default_rng(0)
    t0 = time.perf_counter()
    xb = rng.standard_normal((N, D), dtype=np.float32)
    xq = rng.standard_normal((NQ, D), dtype=np.float32)
    res["data_gen_seconds"] = round(time.perf_counter() - t0, 2)
    res["database_bytes"] = int(xb.nbytes)
    res["database_GB"] = round(xb.nbytes / 1e9, 3)
    res["rss_after_data_GB"] = round(rss_gb(), 2)

    # ---- flat inner product ------------------------------------------------------
    flat = {"load_code": "index = faiss.IndexFlatIP(256); index.add(xb)"}
    t0 = time.perf_counter()
    index = faiss.IndexFlatIP(D)
    index.add(xb)
    flat["build_seconds"] = round(time.perf_counter() - t0, 3)
    flat["ntotal"] = index.ntotal
    flat["rss_after_build_GB"] = round(rss_gb(), 2)

    t0 = time.perf_counter()
    Dis, Ind = index.search(xq, K)
    flat["search_seconds"] = round(time.perf_counter() - t0, 3)
    flat["ms_per_query"] = round(1000 * flat["search_seconds"] / NQ, 3)
    flat["qps"] = round(NQ / flat["search_seconds"], 1)
    flat["result_shapes"] = [list(Dis.shape), list(Ind.shape)]
    flat["index_bytes_in_ram_est"] = int(xb.nbytes)  # IndexFlat stores the raw vectors
    res["IndexFlatIP"] = flat
    gt = Ind.copy()

    # ---- IVFPQ -------------------------------------------------------------------
    nlist, m, nbits = 4096, 32, 8
    ivf = {"nlist": nlist, "m_subquantizers": m, "nbits": nbits,
           "load_code": (f'quant = faiss.IndexFlatIP({D})\n'
                         f'index = faiss.IndexIVFPQ(quant, {D}, {nlist}, {m}, {nbits}, '
                         f'faiss.METRIC_INNER_PRODUCT)\n'
                         'index.train(xb[:262144]); index.add(xb); index.nprobe = 32')}
    try:
        quant = faiss.IndexFlatIP(D)
        ix = faiss.IndexIVFPQ(quant, D, nlist, m, nbits, faiss.METRIC_INNER_PRODUCT)
        ntrain = 262_144
        t0 = time.perf_counter()
        ix.train(xb[:ntrain])
        ivf["train_seconds"] = round(time.perf_counter() - t0, 2)
        ivf["n_train_vectors"] = ntrain

        t0 = time.perf_counter()
        ix.add(xb)
        ivf["add_seconds"] = round(time.perf_counter() - t0, 2)
        ivf["build_seconds"] = round(ivf["train_seconds"] + ivf["add_seconds"], 2)
        ivf["ntotal"] = ix.ntotal
        ivf["rss_after_build_GB"] = round(rss_gb(), 2)
        ivf["codes_bytes_est"] = N * m          # 1 byte per subquantizer at nbits=8
        ivf["codes_MB_est"] = round(N * m / 1e6, 1)
        ivf["compression_vs_flat"] = f"{xb.nbytes / (N * m):.1f}x"

        for nprobe in (8, 32, 128):
            ix.nprobe = nprobe
            t0 = time.perf_counter()
            _, I2 = ix.search(xq, K)
            dt = time.perf_counter() - t0
            # recall@K against the exact flat result
            inter = sum(len(set(a) & set(b)) for a, b in zip(I2, gt))
            ivf[f"nprobe_{nprobe}"] = {
                "search_seconds": round(dt, 3),
                "ms_per_query": round(1000 * dt / NQ, 3),
                "qps": round(NQ / dt, 1),
                "recall_at_32_vs_flat": round(inter / (NQ * K), 4),
            }
        ivf["status"] = "PASS"
    except Exception as e:
        ivf["status"] = "FAIL"
        ivf["error"] = f"{type(e).__name__}: {e}"
    res["IndexIVFPQ"] = ivf
    res["peak_rss_GB"] = round(rss_gb(), 2)
    res["status"] = "PASS" if ivf.get("status") == "PASS" else "PARTIAL"

    print(json.dumps(res, indent=2))
    jdump("07_faiss", res)


if __name__ == "__main__":
    main()
