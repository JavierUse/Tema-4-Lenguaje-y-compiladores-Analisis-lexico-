%{
#include <stdio.h>
%}

%option noyywrap

%%
"let"           { printf("TOKEN: LET, Lexema: %s\n", yytext); }
"mut"           { printf("TOKEN: MUT, Lexema: %s\n", yytext); }
"fn"            { printf("TOKEN: FN, Lexema: %s\n", yytext); }
"i32"           { printf("TOKEN: TIPO_INT, Lexema: %s\n", yytext); }
"true"|"false"  { printf("TOKEN: BOOLEANO, Lexema: %s\n", yytext); }
[0-9]+          { printf("TOKEN: NUMERO, Lexema: %s\n", yytext); }
[a-zA-Z_][a-zA-Z0-9_]* { printf("TOKEN: IDENTIFICADOR, Lexema: %s\n", yytext); }
"="             { printf("TOKEN: ASIGNACION, Lexema: %s\n", yytext); }
"+"             { printf("TOKEN: SUMA, Lexema: %s\n", yytext); }
";"             { printf("TOKEN: PUNTO_COMA, Lexema: %s\n", yytext); }
[ \t\r\n]+     { /* Ignorar espacios y saltos */ }
"{"             { printf("TOKEN: LLAVE_ABRE, Lexema: %s\n", yytext); }
"}"             { printf("TOKEN: LLAVE_CIERRA, Lexema: %s\n", yytext); }
.               { printf("ERROR LÉXICO: Carácter no reconocido: %s\n", yytext); }
%%

int main(int argc, char **argv) {
    if (argc > 1) {
        yyin = fopen(argv[1], "r");
        if (!yyin) { perror("Error al abrir archivo"); return 1; }
    }
    yylex();
    return 0;
}