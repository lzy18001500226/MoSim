// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <isaacsim/core/includes/core/Platform.h>
#include <isaacsim/core/includes/math/core/Core.h>
#include <isaacsim/core/includes/math/core/Types.h>

#include <algorithm>
#include <ctype.h>
#include <fstream>
#include <iostream>
#include <stdio.h>
#include <string.h>
#include <string>


#if defined(_WIN32) || defined(_WIN64)

// clang-format off
#    include <windows.h>
#    include <commdlg.h>
#    include <mmsystem.h>
// clang-format on

void Sleep(double seconds)
{
    ::Sleep(DWORD(seconds * 1000));
}

//// helper function to get exe path
// string GetExePath()
//{
//	const uint32_t kMaxPathLength = 2048;
//
//	char exepath[kMaxPathLength];
//
//	// get exe path for file system
//	uint32_t i = GetModuleFileName(NULL, exepath, kMaxPathLength);
//
//	// rfind first slash
//	while (i && exepath[i] != '\\' && exepath[i] != '//')
//		i--;
//
//	// insert null terminater to cut off exe name
//	return string(&exepath[0], &exepath[i+1]);
//}
//
// string FileOpenDialog(char *filter)
//{
//	HWND owner=NULL;
//
//	OPENFILENAME ofn;
//	char fileName[MAX_PATH] = "";
//	ZeroMemory(&ofn, sizeof(ofn));
//	ofn.lStructSize = sizeof(OPENFILENAME);
//	ofn.hwndOwner = owner;
//	ofn.lpstrFilter = filter;
//	ofn.lpstrFile = fileName;
//	ofn.nMaxFile = MAX_PATH;
//	ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_HIDEREADONLY |
// OFN_NOCHANGEDIR; 	ofn.lpstrDefExt = "";
//
//	string fileNameStr;
//
//	if ( GetOpenFileName(&ofn) )
//		fileNameStr = fileName;
//
//	return fileNameStr;
//}
//
// bool FileMove(const char* src, const char* dest)
//{
//	BOOL b = MoveFileEx(src, dest, MOVEFILE_REPLACE_EXISTING);
//	return b == TRUE;
//}
//
// bool FileScan(const char* pattern, vector<string>& files)
//{
//	HANDLE          h;
//	WIN32_FIND_DATA info;
//
//	// build a list of files
//	h = FindFirstFile(pattern, &info);
//
//	if (h != INVALID_HANDLE_VALUE)
//	{
//		do
//		{
//			if (!(strcmp(info.cFileName, ".") == 0 ||
// strcmp(info.cFileName, "..") == 0))
//			{
//				files.push_back(info.cFileName);
//			}
//		}
//		while (FindNextFile(h, &info));
//
//		if (GetLastError() != ERROR_NO_MORE_FILES)
//		{
//			return false;
//		}
//
//		FindClose(h);
//	}
//	else
//	{
//		return false;
//	}
//
//	return true;
//}

#else

// linux, mac platforms
#    include <sys/time.h>


#endif
using namespace std;
