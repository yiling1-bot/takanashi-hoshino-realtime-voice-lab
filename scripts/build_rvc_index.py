from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import faiss
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--exp", required=True)
    parser.add_argument("--version", default="v2", choices=["v1", "v2"])
    args = parser.parse_args()

    exp_dir = args.repo / "logs" / args.exp
    feature_dir = exp_dir / ("3_feature256" if args.version == "v1" else "3_feature768")
    outside_index_root = args.repo / "assets" / "indices"
    outside_index_root.mkdir(parents=True, exist_ok=True)

    feature_files = sorted(feature_dir.glob("*.npy"))
    if not feature_files:
        raise RuntimeError(f"No feature files found in {feature_dir}")

    npys = [np.load(path) for path in feature_files]
    big_npy = np.concatenate(npys, axis=0)
    order = np.arange(big_npy.shape[0])
    np.random.shuffle(order)
    big_npy = big_npy[order].astype(np.float32)

    total_fea = exp_dir / "total_fea.npy"
    np.save(total_fea, big_npy)

    dim = 256 if args.version == "v1" else 768
    n_ivf = min(int(16 * np.sqrt(big_npy.shape[0])), big_npy.shape[0] // 39)
    n_ivf = max(n_ivf, 1)

    index = faiss.index_factory(dim, f"IVF{n_ivf},Flat")
    index_ivf = faiss.extract_index_ivf(index)
    index_ivf.nprobe = 1

    print(f"features={big_npy.shape}")
    print(f"n_ivf={n_ivf}")
    print("training index...")
    index.train(big_npy)

    trained = exp_dir / f"trained_IVF{n_ivf}_Flat_nprobe_{index_ivf.nprobe}_{args.exp}_{args.version}.index"
    faiss.write_index(index, str(trained))

    print("adding features...")
    batch_size = 8192
    for start in range(0, big_npy.shape[0], batch_size):
        index.add(big_npy[start : start + batch_size])

    added = exp_dir / f"added_IVF{n_ivf}_Flat_nprobe_{index_ivf.nprobe}_{args.exp}_{args.version}.index"
    faiss.write_index(index, str(added))

    outside = outside_index_root / f"{args.exp}_IVF{n_ivf}_Flat_nprobe_{index_ivf.nprobe}_{args.exp}_{args.version}.index"
    shutil.copyfile(added, outside)

    print(f"trained_index={trained}")
    print(f"added_index={added}")
    print(f"outside_index={outside}")


if __name__ == "__main__":
    main()
