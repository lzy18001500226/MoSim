#include<stdio.h>

int add(int a, int b){
  int c;
  c = a + b;
  return c;
}

int main(){
  int c;
  c = add(1,2);
  printf("1 + 2 = %d\n", c);
}
