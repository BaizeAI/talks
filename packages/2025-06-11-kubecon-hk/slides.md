---
layout: center
highlighter: shiki
css: unocss
colorSchema: dark
transition: fade-out
title: Taming Dependency Chaos for LLM in K8S
exportFilename: KubeCon HK 2025.06 - Taming Dependency Chaos for LLM in K8S
lineNumbers: false
drawings:
  persist: false
mdc: true
clicks: 0
preload: false
glowSeed: 229
routerMode: hash
---

<div translate-x--14>

<h1>
  Taming Dependency Chaos for LLM in K8S
</h1>

DaoCloud Fanshi Zhang, Kebe Liu, Peter Pan

</div>

<div w-full absolute bottom-0 left-0 flex items-center transform="translate-x--10 translate-y--10">
  <div w-full flex items-center justify-end gap-4>
    <img src="/KubeCon.svg" h-20 translate-y-4>
  </div>
</div>

---
layout: intro
class: px-24
glowSeed: 205
---

<div flex items-center justify-center>
  <div
    v-click flex flex-col gap-2 items-center justify-center transition duration-500 ease-in-out
    :class="$clicks < 1 ? 'translate-x--20 opacity-0' : 'translate-x-0 opacity-100'"
  >
    <div flex items-center gap-6>
      <img src="/DaoCloud.svg" h-40 />
    </div>
  </div>
  <div
    v-after pl-15 pr-15 transition duration-500 ease-in-out
    :class="$clicks < 1 ? 'scale-80' : 'scale-100'"
  >
    <div i-carbon:close text-8xl />
  </div>
  <div
    v-after flex flex-col gap-2 items-center justify-center transition duration-500 ease-in-out
    :class="$clicks < 1 ? 'translate-x-20 opacity-0' : 'translate-x-0 opacity-100'"
  >
    <div flex items-center gap-6>
      <div i-devicon:kubernetes inline-block text-6xl /> <span text-4xl text="[#5791f7]">Kubernetes</span>
    </div>
  </div>
</div>

---
layout: intro
class: px-35
glowSeed: 205
---

<div flex>
  <div
    v-click="1" flex flex-col items-center transition duration-500 ease-in-out
    :class="$clicks < 1 ? 'translate-y-20 opacity-0' : 'translate-y-0 opacity-100'"
  >
    <img src="/person/peter.png" w-50 h-50 rounded-full object-cover mb-5>
    <span font-semibold text-3xl >Peter Pan</span>
    <div items-center>
      <div>
        <span class="opacity-70">Software Engineering VP</span>
      </div>
      <div text-sm flex items-center justify-center gap-2 mt-4>
        <div i-ri:github-fill /><span underline decoration-dashed font-mono decoration-zinc-300>panpan0000</span>
      </div>
    </div>
  </div>
  <div flex-1 />
  <div
    v-click="2" flex flex-col items-center transition duration-500 ease-in-out
    :class="$clicks < 2 ? 'translate-y-20 opacity-0' : 'translate-y-0 opacity-100'"
  >
    <img src="/person/kebe.jpeg" w-50 h-50 rounded-full object-cover mb-5>
    <span font-semibold text-3xl>Kebe Liu</span>
    <div items-center>
      <div>
        <span class="opacity-70">Senior software engineer</span>
      </div>
      <div text-sm flex items-center justify-center gap-2 mt-4>
        <div i-ri:github-fill /><span underline decoration-dashed font-mono decoration-zinc-300>kebe7jun</span>
      </div>
    </div>
  </div>
  <div flex-1 />
  <div
    v-click="3" flex flex-col items-center transition duration-500 ease-in-out
    :class="$clicks < 3 ? 'translate-y-20 opacity-0' : 'translate-y-0 opacity-100'"
  >
    <img src="/person/neko.jpeg" w-50 h-50 rounded-full object-cover mb-5>
    <span font-semibold text-3xl>Fanshi Zhang</span>
    <div flex-col items-center>
      <div>
        <span class="opacity-70">Senior software engineer</span>
      </div>
      <div text-sm flex items-center justify-center gap-2 mt-4>
        <div i-ri:github-fill /><span underline decoration-dashed font-mono decoration-zinc-300>nekomeowww</span>
      </div>
    </div>
  </div>
</div>

---
layout: center
class: text-center
---

# "It Works On My Machine"™: The ML Engineer's Lament

<div class="mt-4 text-xl opacity-80">
  How many times have you seen this?
</div>

<div class="mt-10 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg px-2 py-1 text-left">

```shell
$ python train.py
ImportError: libcudart.so.11.0: cannot open shared object file
$ pip install torch --index-url https://download.pytorch.org/whl/cu118
RuntimeError: CUDA error: no kernel image is available for execution
$ ldd $(which python3) | grep 'not found'
        libstdc++.so.6 => not found</pre>
```

</div>

---
layout: center
---

# Dependency Hell: When Python Meets C++

<div v-click class="mt-10">
  <div class="relative">
    <div class="w-full h-full flex items-center justify-center">
      <div class="text-6xl i-logos:python" />
    </div>
    <div class="w-full h-full flex items-center justify-center">
      <div class="text-6xl i-logos:c-plusplus" />
    </div>
    <div class="w-full h-full">
      <div class="text-8xl i-carbon:warning-alt" />
    </div>
  </div>
</div>

<div v-click class="mt-10">
  <h3>The Perfect Storm: When Python Code Meets C++ Underpinnings</h3>
</div>

---
layout: two-cols
class: px-2
---

# The Silent Saboteurs

<div class="mt-4">
  <h3>Root Causes</h3>
  <div class="space-y-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <div class="flex items-center gap-2">
      <div i-carbon:checkmark class="text-sky-300" />
      <span>ABI incompatibility between C++ versions</span>
    </div>
    <div class="flex items-center gap-2">
      <div i-carbon:checkmark class="text-sky-300" />
      <span>CUDA driver/runtime version mismatch</span>
    </div>
    <div class="flex items-center gap-2">
      <div i-carbon:checkmark class="text-sky-300" />
      <span>System library conflicts</span>
    </div>
    <div class="flex items-center gap-2">
      <div i-carbon:checkmark class="text-sky-300" />
      <span>Package version inconsistencies</span>
    </div>
  </div>
</div>

<div class="mt-8">
  <h3>Real-World Impact</h3>
  <div class="space-y-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <div class="flex items-center gap-2 text-red-400">
      <div i-carbon:warning />
      <span>Hours wasted reinstalling CUDA</span>
    </div>
    <div class="flex items-center gap-2 text-red-400">
      <div i-carbon:warning />
      <span>Inconsistent results across environments</span>
    </div>
    <div class="flex items-center gap-2 text-red-400">
      <div i-carbon:warning />
      <span>Production deployments that mysteriously fail</span>
    </div>
  </div>
</div>

::right::

<div class="pl-4">
  <div class="mt-4">
    <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
      <h4>Example: PyTorch Build Matrix</h4>
      <pre class="text-xs mt-2">
CUDA_VERSION=11.8.0
CUDNN_VERSION=8.7.0
NCCL_VERSION=2.16.5
GCC_VERSION=9.4.0
PYTHON_VERSION=3.10
      </pre>
    </div>
  </div>

  <div class="mt-8">
    <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
      <h4>The Hidden Dependencies</h4>
      <pre class="text-xs mt-2">
$ ldd /usr/local/lib/python3.10/site-packages/torch/lib/libtorch_cuda.so
  libcudart.so.11.0 => not found
  libcufft.so.10 => not found
  libcurand.so.10 => not found
  libcusolver.so.11 => not found
  libcusparse.so.11 => not found
      </pre>
    </div>
  </div>
</div>

---
layout: center
---

# The Hidden Iceberg: What pip Can't See

<div class="mt-4 grid grid-cols-2 gap-8">
  <div v-click class="relative">
    <div class="relative h-80">
      <div class="absolute bottom-0 w-full bg-blue-500/20 h-60 rounded-t-full"></div>
      <div class="absolute top-0 w-full">
        <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
          <h3 class="mb-4">Visible Surface</h3>
          <code class="text-sm">
            torch==2.1.0<br>
            transformers==4.36.0<br>
            accelerate==0.25.0
          </code>
        </div>
      </div>
      <div v-click class="absolute bottom-0 w-full">
        <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
          <h3 class="mb-4">Hidden Depths</h3>
          <code class="text-xs">
            CUDA 11.8<br>
            gcc 9.4.0<br>
            cmake 3.22.1<br>
            libnccl2<br>
            libcudnn8<br>
            cuda-cupti-dev<br>
            ...and dozens more
          </code>
        </div>
      </div>
    </div>
  </div>

  <div v-click class="space-y-4">
    <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
      <h3 class="mb-2">Python Package Managers</h3>
      <ul class="space-y-2 text-sm">
        <li class="flex items-center gap-2">
          <div i-carbon:checkmark class="text-green-400" />
          <span>Handle Python dependencies well</span>
        </li>
        <li class="flex items-center gap-2">
          <div i-carbon:close class="text-red-400" />
          <span>Blind to underlying C++ libraries</span>
        </li>
        <li class="flex items-center gap-2">
          <div i-carbon:close class="text-red-400" />
          <span>No system-level dependency management</span>
        </li>
      </ul>
    </div>

    <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
      <h3 class="mb-2">The Reality</h3>
      <p class="text-sm opacity-80">Modern ML libraries are just thin Python wrappers around massive C++ and CUDA codebases</p>
    </div>
  </div>
</div>

---
layout: center
---

# CUDA Conundrum: The Version Wars

<div class="grid grid-cols-3 gap-4 mt-6">
  <div v-click class="flex flex-col items-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="text-4xl mb-4">🎯</div>
    <h3>Version 11.8</h3>
    <p class="text-sm opacity-70">PyTorch's Choice</p>
    <p class="text-xs mt-2 text-green-300">Optimized for current models</p>
  </div>
  <div v-click class="flex flex-col items-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="text-4xl mb-4">🎯</div>
    <h3>Version 12.1</h3>
    <p class="text-sm opacity-70">System Default</p>
    <p class="text-xs mt-2 text-yellow-300">Newest features, compatibility issues</p>
  </div>
  <div v-click class="flex flex-col items-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="text-4xl mb-4">🎯</div>
    <h3>Version 11.6</h3>
    <p class="text-sm opacity-70">Legacy Model</p>
    <p class="text-xs mt-2 text-red-300">Required by older frameworks</p>
  </div>
</div>

<div v-click class="mt-8 grid grid-cols-2 gap-4">
  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <h3 class="mb-2">CUDA Complexity</h3>
    <ul class="space-y-1 text-sm">
      <li>• Driver vs Runtime version mismatch</li>
      <li>• cuDNN compatibility matrix</li>
      <li>• NCCL version requirements</li>
    </ul>
  </div>

  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <h3 class="mb-2">The Silent Killer</h3>
    <p class="text-sm text-red-400">Often fails with cryptic errors or worse - <span class="font-bold">silent numerical errors</span> in your models</p>
  </div>
</div>

---
layout: center
---

# Compiler Chaos: When gcc Versions Wage War

<div class="mt-6 grid grid-cols-2 gap-8">
  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3 class="mb-4">The C++ ABI Battle</h3>
    <div class="text-sm space-y-4">
      <div class="flex items-center gap-2">
        <div i-logos:gcc text-2xl />
        <span>gcc 9.4.0 required by PyTorch</span>
      </div>
      <div class="flex items-center gap-2">
        <div i-logos:gcc text-2xl />
        <span>gcc 11.0 installed on system</span>
      </div>
      <div class="mt-4 text-red-400">
        Result: Binary incompatibility at runtime
      </div>
    </div>
  </div>

  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3 class="mb-4">Real-World Errors</h3>
    <div class="space-y-4 text-sm">
      <code class="block p-2 bg-black/30 rounded text-red-300">
ImportError: /lib64/libstdc++.so.6: version<br>'GLIBCXX_3.4.29' not found
      </code>
      <code class="block p-2 bg-black/30 rounded text-red-300">
undefined symbol: _ZN3c10...<br>(C++ name mangling errors)
      </code>
      <div class="mt-4">
        <span class="text-yellow-300">Most frustrating part:</span> Different errors on different machines
      </div>
    </div>
  </div>
</div>

<div v-click class="mt-8 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
  <h3 class="text-center mb-2">The Developer Experience</h3>
  <div class="grid grid-cols-3 gap-4 text-sm text-center">
    <div>
      <div class="text-xl mb-2">👩‍💻</div>
      <p>"Works on my laptop"</p>
    </div>
    <div>
      <div class="text-xl mb-2">👨‍💻</div>
      <p>"Crashes on my desktop"</p>
    </div>
    <div>
      <div class="text-xl mb-2">🖥️</div>
      <p>"Different results in production"</p>
    </div>
  </div>
</div>

---
layout: center
---

# Why Reusable Environments Matter

<div class="mt-6 grid grid-cols-2 gap-8">
  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3 class="mb-4">Traditional Workflow Pain</h3>
    <div class="space-y-4 text-sm">
      <div class="flex items-center gap-2 text-red-400">
        <div i-carbon:warning />
        <span>Scientists and engineers with different setups</span>
      </div>
      <div class="flex items-center gap-2 text-red-400">
        <div i-carbon:warning />
        <span>Hours reinstalling CUDA for each training run</span>
      </div>
      <div class="flex items-center gap-2 text-red-400">
        <div i-carbon:warning />
        <span>Notebooks vs. production environment mismatch</span>
      </div>
      <div class="flex items-center gap-2 text-red-400">
        <div i-carbon:warning />
        <span>"Works in dev, fails in prod" syndrome</span>
      </div>
    </div>
  </div>

  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3 class="mb-4">The Better Way</h3>
    <div class="space-y-4 text-sm">
      <div class="flex items-center gap-2 text-green-400">
        <div i-carbon:checkmark-outline />
        <span>One environment definition, everywhere</span>
      </div>
      <div class="flex items-center gap-2 text-green-400">
        <div i-carbon:checkmark-outline />
        <span>Install once, mount instantly</span>
      </div>
      <div class="flex items-center gap-2 text-green-400">
        <div i-carbon:checkmark-outline />
        <span>Identical experience across team members</span>
      </div>
      <div class="flex items-center gap-2 text-green-400">
        <div i-carbon:checkmark-outline />
        <span>Seamless dev-to-prod workflow</span>
      </div>
    </div>
  </div>
</div>

<div v-click class="mt-8 text-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
  <p class="text-xl">From <span class="text-red-400">hours of setup frustration</span> to <span class="text-green-400">seconds of mounting</span></p>
</div>

---
layout: center
---

# The Usual Suspects: Tools We've Tried

<div class="mt-6 grid grid-cols-3 gap-4">
  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="flex items-center gap-3 mb-4">
      <div i-devicon:python class="text-3xl" />
      <h3 class="text-xl">pip & uv</h3>
    </div>
    <ul class="space-y-2 text-sm opacity-80">
      <li>• Fast for Python packages</li>
      <li class="text-red-400">• Blind to C++/CUDA deps</li>
      <li class="text-red-400">• No system library management</li>
      <li class="text-red-400">• Version conflicts common</li>
    </ul>
  </div>
  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="flex items-center gap-3 mb-4">
      <div i-devicon:docker class="text-3xl" />
      <h3 class="text-xl">Docker</h3>
    </div>
    <ul class="space-y-2 text-sm opacity-80">
      <li>• Reproducible environments</li>
      <li class="text-red-400">• Massive image sizes (5-10GB)</li>
      <li class="text-red-400">• Slow build times (30+ min)</li>
      <li class="text-red-400">• Resource intensive</li>
    </ul>
  </div>
  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="flex items-center gap-3 mb-4">
      <div i-devicon:nixos class="text-3xl" />
      <h3 class="text-xl">Nix</h3>
    </div>
    <ul class="space-y-2 text-sm opacity-80">
      <li>• Complete reproducibility</li>
      <li class="text-red-400">• PhD-level learning curve</li>
      <li class="text-red-400">• Complex configuration</li>
      <li class="text-red-400">• K8s integration challenges</li>
    </ul>
  </div>
</div>

<div v-click class="mt-8 text-center">
  <h3 class="mb-2">What We Need</h3>
  <div class="inline-block bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <ul class="flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm">
      <li class="flex items-center gap-1"><div i-carbon:checkmark class="text-green-400" /> Python package management</li>
      <li class="flex items-center gap-1"><div i-carbon:checkmark class="text-green-400" /> C++/CUDA awareness</li>
      <li class="flex items-center gap-1"><div i-carbon:checkmark class="text-green-400" /> Storage efficiency</li>
      <li class="flex items-center gap-1"><div i-carbon:checkmark class="text-green-400" /> Fast setup times</li>
      <li class="flex items-center gap-1"><div i-carbon:checkmark class="text-green-400" /> K8s native</li>
    </ul>
  </div>
</div>

---
glowSeed: 12129
---

# Introducing Datasets: The Solution

<div class="mt-10 flex justify-center">
  <div class="relative w-120 h-60">
    <div v-click class="absolute inset-0 flex items-center justify-center">
      <div class="text-[150px] i-logos:kubernetes" />
    </div>
    <div v-click class="absolute top-17 left--4">
      <div class="text-7xl i-logos:python" />
    </div>
    <div v-click class="absolute top-18 right--16">
      <div class="text-4xl i-logos:conda" />
    </div>
    <div v-click class="absolute bottom--4 left-8">
      <div class="text-[100px] i-devicon:docker" />
    </div>
    <div v-click class="absolute bottom-4 right--8">
      <div class="text-4xl i-logos:nvidia" />
    </div>
  </div>
</div>

<div v-click class="mt-8 text-center">
  <h3>One solution to rule them all</h3>
  <p class="opacity-70">Python + C++ + CUDA harmony in Kubernetes</p>
</div>

---

# One CRD to Rule Them All

<div class="flex relative">

<div class="mt-2 w-75%">
  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg pl-1 pr-1">

```yaml
apiVersion: dataset.baize.io/v1alpha1
kind: Dataset
metadata:
  name: pytorch-env
spec:
  source:
    type: CONDA
    uri: conda://python?version=3.11.9
    options:
      packageManager: CONDA
      pythonVersion: 3.11.9
      condaEnvironmentYml: |-
        channels: ['nvidia', 'conda-forge']
        dependencies: [
          - 'cuda'
          - 'cuda-libraries-dev'
          - 'cuda-nvcc'
          - 'cuda-nvtx'
          - 'cuda-cupti'
      pipRequirementsTxt: |-
        transformers==4.35.0
        torch
        torchaudio
        torchvision
```

  </div>
</div>

<div class="absolute right-0 top-25">
  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <div text-xl text-neutral-300>Key Features</div>
    <ul class="mt-4">
      <li>• Multi-source support (<code>conda</code>, <code>huggingface</code>)</li>
      <li>• Self-contained enterprise model hub</li>
      <li>• Pre-loaded datasets and models</li>
      <li>• Install once, use everywhere</li>
      <li>• Secure credential management</li>
    </ul>
  </div>
</div>

</div>

---
layout: two-cols
class: px-2
---

# X-Ray Vision: Datasets Architecture

<div class="mt-4">
  <h3>Controller Architecture</h3>
  <div class="space-y-4">
    <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
      <h4>Reconciliation Loop</h4>
      <pre class="text-xs mt-2">
1. Parse Dataset CRD & validate spec
2. Check source type & credentials
3. Create/update PVC with JuiceFS
4. Deploy init container for setup
5. Download/sync data from source
6. Configure mount options
7. Update dataset status</pre>
    </div>
  </div>
</div>

<div class="mt-6">
  <h3>Multi-Source Support</h3>
  <ul class="mt-2 space-y-1 text-sm">
    <li class="flex items-center gap-2">
      <div i-logos:python class="text-xl" />
      <span>CONDA environments</span>
    </li>
    <li class="flex items-center gap-2">
      <div i-logos:huggingface class="text-xl" />
      <span>HuggingFace models</span>
    </li>
    <li class="flex items-center gap-2">
      <div i-carbon:cloud class="text-xl" />
      <span>Custom repositories</span>
    </li>
  </ul>
</div>

::right::

<div class="pl-4">
  <div class="mt-4">
    <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
      <h4>Implementation Highlights</h4>
      <ul class="mt-2 space-y-2 text-sm">
        <li>• Built on JuiceFS for shared storage</li>
        <li>• CUDA-aware environment resolution</li>
        <li>• Intelligent caching of built packages</li>
        <li>• Deduplication of common libraries</li>
      </ul>
    </div>
  </div>

  <div class="mt-6">
    <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
      <h4>Security & Performance</h4>
      <ul class="mt-2 space-y-2 text-sm">
        <li>• RBAC integration with K8s</li>
        <li>• Package verification via checksums</li>
        <li>• Parallel downloads and processing</li>
        <li>• Incremental updates</li>
      </ul>
    </div>
  </div>
</div>

---

# Enterprise Model Hub in Minutes

<div class="mt-6 grid grid-cols-2 gap-8">
  <div v-click class="relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 z-10">
    <h3 class="mb-4">Model Management</h3>
    <ul class="space-y-3 text-sm">
      <li class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Self-contained model registry</span>
      </li>
      <li class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Pre-loading from external sources</span>
      </li>
      <li class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Version control for model weights</span>
      </li>
      <li class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Automatic metadata extraction</span>
      </li>
    </ul>
  </div>

  <div v-click class="relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 z-20 translate-y-4">
    <h3 class="mb-4">Ready Before You Are</h3>
    <ul class="space-y-3 text-sm">
      <li class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Datasets available before training starts</span>
      </li>
      <li class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Environment ready for immediate use</span>
      </li>
      <li class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>No waiting for CUDA compilation</span>
      </li>
      <li class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Consistent across notebook and training jobs</span>
      </li>
    </ul>
  </div>
</div>

<div v-click class="mt-10 text-center">
  <div class="inline-block bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <p class="text-xl">From <span class="text-red-400">isolated silos</span> to <span class="text-green-400">unified model ecosystem</span></p>
  </div>
</div>

---
layout: center
---

# Dataloader: The Polyglot Dependency Manager

<div class="mt-6 grid grid-cols-2 gap-8">
  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="flex items-center gap-3 mb-4">
      <div i-carbon:terminal class="text-2xl text-sky-300" />
      <h3 class="text-xl">Core Commands</h3>
    </div>
    <div class="space-y-3 text-sm">
      <div class="flex items-center gap-2">
        <code class="bg-black/30 px-2 py-1 rounded">dataloader init</code>
        <span class="opacity-70">Environment setup</span>
      </div>
      <div class="flex items-center gap-2">
        <code class="bg-black/30 px-2 py-1 rounded">dataloader install</code>
        <span class="opacity-70">Dependency resolution</span>
      </div>
      <div class="flex items-center gap-2">
        <code class="bg-black/30 px-2 py-1 rounded">dataloader sync</code>
        <span class="opacity-70">State synchronization</span>
      </div>
      <div class="flex items-center gap-2">
        <code class="bg-black/30 px-2 py-1 rounded">dataloader verify</code>
        <span class="opacity-70">Dependency verification</span>
      </div>
    </div>
  </div>

  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3 class="mb-4">Language Support</h3>
    <div class="grid grid-cols-2 gap-4 text-sm">
      <div>
        <div class="font-semibold mb-1">Python</div>
        <ul class="space-y-1 opacity-80">
          <li>• pip requirements</li>
          <li>• conda environments</li>
          <li>• poetry support</li>
        </ul>
      </div>
      <div>
        <div class="font-semibold mb-1">C++ & System</div>
        <ul class="space-y-1 opacity-80">
          <li>• CUDA versions</li>
          <li>• compiler toolchains</li>
          <li>• system libraries</li>
        </ul>
      </div>
    </div>
    <div class="mt-4 pt-4 border-t border-white/10">
      <div class="font-semibold mb-1">Example: Install PyTorch with CUDA</div>
      <pre class="text-xs bg-black/30 p-2 rounded">
$ dataloader install --cuda=11.8 --torch=2.1.0
[INFO] Resolving compatible C++ runtime...
[INFO] Setting up CUDA environment...
[INFO] Installing PyTorch dependencies...
      </pre>
    </div>
  </div>
</div>

---
layout: center
---

# Smart Dependency Resolution: Solving the Version Maze

<div class="mt-6 relative">
  <div v-click class="absolute top-0 left-0 w-2/3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 z-10">
    <h3>Before Installation</h3>
    <div class="mt-4 space-y-2">
      <div class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Dependency graph analysis</span>
      </div>
      <div class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Version compatibility check</span>
      </div>
      <div class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>System requirements validation</span>
      </div>
      <div class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>C++/CUDA ABI verification</span>
      </div>
    </div>
  </div>

  <div v-click class="absolute top-10 right-0 w-2/3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 z-20">
    <h3>During Installation</h3>
    <div class="mt-4 space-y-2">
      <div class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Parallel downloads</span>
      </div>
      <div class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Incremental builds</span>
      </div>
      <div class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Cache optimization</span>
      </div>
      <div class="flex items-center gap-2">
        <div i-carbon:checkmark-outline class="text-green-400" />
        <span>Conflict resolution</span>
      </div>
    </div>
  </div>

  <!-- Spacer to ensure proper layout height -->
  <div class="h-60"></div>
</div>

<div v-click class="mt-12 text-center">
  <div class="inline-block bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <h3>Resolution Example</h3>
    <pre class="text-xs text-left mt-2">
$ dataloader install torch==2.1.0
[INFO] Detected CUDA requirement: 11.8
[INFO] Detected cuDNN requirement: 8.7.0
[INFO] Detected GCC requirement: 9.4.0
[INFO] Building compatible environment...
    </pre>
  </div>
</div>

---
layout: center
---

# Cache Strategy: Optimizing the Unbearable Heaviness of Builds

<div class="mt-6">
  <div class="relative">
    <div v-click class="absolute inset-0 flex items-center justify-center">
      <div class="w-80 h-80 rounded-full border-4 border-blue-500/30 animate-ping" />
    </div>
    <div class="grid grid-cols-3 gap-4">
      <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
        <h3>Layer 1: Downloads</h3>
        <p class="text-sm opacity-80 mt-2">Source packages & archives</p>
        <ul class="mt-4 text-xs space-y-1 opacity-70">
          <li>• SHA256 verification</li>
          <li>• Mirror fallback</li>
          <li>• Parallel fetching</li>
        </ul>
      </div>
      <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
        <h3>Layer 2: Builds</h3>
        <p class="text-sm opacity-80 mt-2">Compiled binaries & wheels</p>
        <ul class="mt-4 text-xs space-y-1 opacity-70">
          <li>• Deduplication</li>
          <li>• Incremental builds</li>
          <li>• ABI versioning</li>
        </ul>
      </div>
      <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
        <h3>Layer 3: Metadata</h3>
        <p class="text-sm opacity-80 mt-2">Environment configs</p>
        <ul class="mt-4 text-xs space-y-1 opacity-70">
          <li>• Dependency tracking</li>
          <li>• Version resolution</li>
          <li>• Activation scripts</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div v-click class="mt-10 grid grid-cols-2 gap-8">
  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <h3 class="mb-2">Traditional Approach</h3>
    <div class="grid grid-cols-2 gap-2 text-sm">
      <div class="text-red-400">CUDA setup: 45-60 min</div>
      <div class="text-red-400">PyTorch install: 20-30 min</div>
    </div>
  </div>

  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <h3 class="mb-2">With Datasets</h3>
    <div class="grid grid-cols-2 gap-2 text-sm">
      <div class="text-green-400">First setup: 10-15 min</div>
      <div class="text-green-400">Subsequent: seconds</div>
    </div>
  </div>
</div>

---
layout: center
---

# PVC Architecture: Storage Strategies for Gigabytes

<div class="mt-6 flex justify-center">
  <div class="relative w-120">
    <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 mb-4">
      <h3>Shared Cache Layer (JuiceFS)</h3>
      <div class="mt-2 text-sm opacity-80">
        ReadWriteMany PVC for common dependencies
      </div>
      <div class="mt-2 grid grid-cols-3 gap-2 text-xs opacity-70">
        <div>• Deduplication</div>
        <div>• Compression</div>
        <div>• Concurrent access</div>
      </div>
    </div>
    <div class="grid grid-cols-2 gap-4">
      <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
        <h3>Training Workloads</h3>
        <div class="mt-2 text-sm opacity-80">
          ReadOnlyMany mount
        </div>
        <pre class="text-xs mt-2 bg-black/30 p-2 rounded">
volumes:
- name: pytorch-env
  persistentVolumeClaim:
    claimName: pytorch-env
    readOnly: true
        </pre>
      </div>
      <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
        <h3>Development Environment</h3>
        <div class="mt-2 text-sm opacity-80">
          ReadOnlyMany mount
        </div>
        <pre class="text-xs mt-2 bg-black/30 p-2 rounded">
volumes:
- name: pytorch-env
  persistentVolumeClaim:
    claimName: pytorch-env
    readOnly: true
        </pre>
      </div>
    </div>
  </div>
</div>

<div v-click class="mt-8 text-center">
  <div class="inline-block bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
    <p class="text-lg">Storage efficiency: <span class="text-green-400">90% reduction</span> compared to individual environments</p>
  </div>
</div>

---
layout: center
---

# Pixi Integration: The Next Evolution

<div class="mt-6 grid grid-cols-2 gap-8">
  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3>Traditional Conda Approach</h3>
    <div class="mt-4">
      <div class="flex items-center gap-2 text-red-400">
        <div i-carbon:time />
        <span>Minutes to hours for environment setup</span>
      </div>
      <div class="mt-2 flex items-center gap-2 text-red-400">
        <div i-carbon:warning />
        <span>Sequential dependency resolution</span>
      </div>
      <div class="mt-2 flex items-center gap-2 text-red-400">
        <div i-carbon:warning />
        <span>Incompatible ABI issues</span>
      </div>
    </div>
    <pre class="mt-4 text-xs bg-black/30 p-2 rounded">
$ conda create -n myenv python=3.10
$ conda install pytorch torchvision
# Waiting... a long time...
    </pre>
  </div>

  <div v-click class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3>With Pixi Integration</h3>
    <div class="mt-4">
      <div class="flex items-center gap-2 text-green-400">
        <div i-carbon:rocket />
        <span>Seconds to minutes for complete setup</span>
      </div>
      <div class="mt-2 flex items-center gap-2 text-green-400">
        <div i-carbon:checkmark-outline />
        <span>Parallel processing of dependencies</span>
      </div>
      <div class="mt-2 flex items-center gap-2 text-green-400">
        <div i-carbon:checkmark-outline />
        <span>Precompiled binaries with correct ABI</span>
      </div>
    </div>
    <pre class="mt-4 text-xs bg-black/30 p-2 rounded">
$ dataloader init --pixi
$ dataloader install --cuda=11.8 --pytorch
# Ready in seconds with Pixi acceleration
    </pre>
  </div>
</div>

<div v-click class="mt-8 text-center">
  <h2 class="text-gradient-primary">10x Faster Environment Setup</h2>
  <p class="mt-2 opacity-80">Powered by Pixi's innovative package management</p>
</div>

---
layout: center
---

# Real World Impact: Numbers Don't Lie

<div class="mt-6 grid grid-cols-3 gap-4">
  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="text-4xl mb-4">⚡️</div>
    <h3>Environment Setup</h3>
    <p class="text-2xl font-bold text-sky-300">5-10x Faster</p>
    <p class="text-sm opacity-70">With shared environments</p>
    <p class="text-xs mt-2">From hours to minutes</p>
  </div>

  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="text-4xl mb-4">💾</div>
    <h3>Storage Efficiency</h3>
    <p class="text-2xl font-bold text-sky-300">90% Reduction</p>
    <p class="text-sm opacity-70">Using JuiceFS dedup</p>
    <p class="text-xs mt-2">10GB → 1GB typical savings</p>
  </div>

  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="text-4xl mb-4">🎯</div>
    <h3>Development Cycle</h3>
    <p class="text-2xl font-bold text-sky-300">75% Shorter</p>
    <p class="text-sm opacity-70">No more environment setup</p>
    <p class="text-xs mt-2">Instant environment activation</p>
  </div>
</div>

<div class="mt-8 grid grid-cols-2 gap-4">
  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="text-4xl mb-4">🔄</div>
    <h3>Team Productivity</h3>
    <p class="text-xl font-bold text-sky-300">Consistent Environments</p>
    <p class="text-sm opacity-70">Same setup for scientists and engineers</p>
    <p class="text-xs mt-2">No more "works on my machine" issues</p>
  </div>

  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <div class="text-4xl mb-4">🚀</div>
    <h3>Model Deployment</h3>
    <p class="text-xl font-bold text-sky-300">Enterprise Model Hub</p>
    <p class="text-sm opacity-70">Self-contained model registry</p>
    <p class="text-xs mt-2">Pre-loaded models ready for inference</p>
  </div>
</div>

---
layout: center
---

# Future Roadmap: Building the Future Together

<div class="mt-6 grid grid-cols-2 gap-8">
  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3>Coming Soon</h3>
    <ul class="mt-4 space-y-2">
      <li>• ModelScope integration</li>
      <li>• Multi-mirror failover system</li>
      <li>• Bandwidth control & QoS</li>
      <li>• Cache prewarming for clusters</li>
      <li>• Enhanced observability</li>
    </ul>
  </div>

  <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3>Long-Term Vision</h3>
    <ul class="mt-4 space-y-2">
      <li>• P2P distribution across nodes</li>
      <li>• Cross-region sync for global teams</li>
      <li>• Automated version lifecycle management</li>
      <li>• Intelligent auto-optimization</li>
      <li>• Extended language ecosystem support</li>
    </ul>
  </div>
</div>

<div class="mt-8 text-center">
  <div class="inline-block bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
    <h3 class="mb-4">Join the Revolution</h3>
    <div class="grid grid-cols-3 gap-8">
      <div class="text-center">
        <div class="text-3xl mb-2">🛠️</div>
        <div class="font-semibold">Contribute</div>
        <p class="text-xs opacity-70">Help build new features</p>
      </div>
      <div class="text-center">
        <div class="text-3xl mb-2">💡</div>
        <div class="font-semibold">Suggest</div>
        <p class="text-xs opacity-70">Share your use cases</p>
      </div>
      <div class="text-center">
        <div class="text-3xl mb-2">🔗</div>
        <div class="font-semibold">Connect</div>
        <p class="text-xs opacity-70">Join our community</p>
      </div>
    </div>
  </div>
</div>

---
class: py-10
---

<div flex>
  <div flex-1>
    <div mt-50 />
    <div text="[48px]">
      Thank you
    </div>
  </div>
  <div text-sm text="zinc-300" text-right flex flex-col gap-3 mt-3>
    <div>
      Slides open sourced at <a href="https://github.com/BaizeAI/talks"><div inline-block mr-1 translate-y-0.8 i-ri:github-fill />github.com/BaizeAI/talks</a>
    </div>
    <div>
      Slides built on top of <a href="https://sli.dev"><div inline-block mr-1 translate-y-0.8 i-logos:slidev />sli.dev</a>
    </div>
    <div self-end mt-16 translate-x-6>
      <img src="/slide_qr.png" w-50 />
    </div>
  </div>
</div>

<div w-full absolute bottom-0 left-0 flex items-center transform="translate-x--10 translate-y--10">
  <div w-full flex items-center justify-end gap-4>
    <img src="/KubeCon.svg" h-20 translate-y-4>
  </div>
</div>
