#!/bin/bash
mkdir -p build
for file in passes/*.cpp; do
  name=$(basename "$file" .cpp)
  echo "→ Compilation de $name"
  clang++ -fPIC -shared \
    -I$(llvm-config --includedir) \
    -o build/$name.so "$file" \
    $(llvm-config --cxxflags --ldflags --system-libs --libs core passes support)
done
