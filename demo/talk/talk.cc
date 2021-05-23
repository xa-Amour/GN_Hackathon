// Copyright 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#include <stdio.h>

#include "talk.h"
#include "subtalk/sub_talk.h"

const char* Talk() {
  printf("call, %s\n", SubTalk());
  return "action talk";
}
