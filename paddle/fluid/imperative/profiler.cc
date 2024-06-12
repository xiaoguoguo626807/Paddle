// Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "paddle/fluid/imperative/profiler.h"

#ifdef WITH_GPERFTOOLS
#include "gperftools/profiler.h"
#endif
#include <glog/logging.h>

#include <mutex>  // NOLINT
#include "paddle/fluid/platform/flags.h"

PADDLE_DEFINE_EXPORTED_string(
    tracer_profile_fname,
    "xxgperf",
    "Profiler filename for imperative tracer, which generated by gperftools."
    "Only valid when compiled `WITH_PROFILER=ON`. Empty if disable.");

namespace paddle::imperative {

static std::once_flag gTracerProfileOnce;
#ifdef WITH_GPERFTOOLS
static bool gTracerProfilerStarted = false;
#endif

void StartProfile() {
  if (!FLAGS_tracer_profile_fname.empty()) {
    std::call_once(gTracerProfileOnce, [] {
#ifdef WITH_GPERFTOOLS
      ProfilerStart(FLAGS_tracer_profile_fname.c_str());
      gTracerProfilerStarted = true;
#else
      LOG(WARNING) << "Paddle is not compiled with gperftools. "
                      "FLAGS_tracer_profile_fname will be ignored";
#endif
    });
  }
}

void StopProfile() {
#ifdef WITH_GPERFTOOLS
  ProfilerFlush();
#else
  LOG(WARNING) << "Paddle is not compiled with gperftools. "
                  "FLAGS_tracer_profile_fname will be ignored";
#endif
}

}  // namespace paddle::imperative
