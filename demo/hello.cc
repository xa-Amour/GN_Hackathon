// Copyright 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <stdio.h>

#include "hello_shared.h"
#include "hello_static.h"
#include "talk/talk.h"

int main(int argc, char* argv[]) {
  printf("%s, %s\n", GetStaticText(), GetSharedText());
  printf("%s, %s\n", GetStaticText(), Talk());
  return 0;
}
