#include <Windows.h>
#include <cstdlib>
#include <filesystem>
#include <cstdio>
int main(void) {
    Sleep(5500);
    if (std::filesystem::exists(".\\main.py")) {
        WinExec("cmd.exe /c \"python -u \".\\main.py\"\"", SW_HIDE);
    } else {
        WinExec("cmd.exe /c \"Mouse Lock.exe\"", SW_HIDE);
    }

    return 0;
}
