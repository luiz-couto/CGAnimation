# CGAnimation
Python implementation of an MD2 file reader, rendering in OpenGL and animation with shape interpolation.
## Overview
Esse projeto tem como objetivo a implementação de um leitor de arquivos .md2, com a finalidade de interpolar entre as frames principais e gerar a animação utilizando OpenGl.

Para acessar o github desse, projeto, basta seguir o link:
> https://github.com/luiz-couto/CGAnimation

Nele, é possível ver todas as etapas de desenvolvimento além do código final.

## Para Compilar
Antes de compilar o código, é necessário a instalação de algumas bibliotecas essenciais:
* OpenGL.GL
* OpenGL.GLU
* OpenGL.GLUT
(Para importar as funcionalidades do OpenGl)
* struct
* ctypes
(Para realizar a conversão de tipos)
* PIL
(Para realizar a texturização - ainda não está funcionando)

Além de, é claro, o python 3.x. Caso você não possua alguma das bibliotecas acima, basta rodar:
```
pip install *nome_da_biblioteca*

```
Para compilar o programa, simplesmente entre na pasta onde está o arquivo *.py* e rode a partir do terminal:
```
python3 main.py

```
## Após a compilação
Depois de compilado corretamente, o programa abrirá a janela com a animação! Lembrando que não foi implementada a texturização, e por isso o objeto(que no caso é um ogro) terá a cor branca. Como são diversas animações, resolvi adicionar um comando para mudar a animação em tempo de execução: Apenas aperte a tecla "C" no teclado para trocar de animação. Quando chegar na última(são ao todo 20) voltará para a primeira. Alguns outros comandos do teclado disponíveis:

- C -> Change animation
- W -> Wireframe View
- S -> Solid View (padrão)
- P -> Points View
- A -> Stop/Run animation
- L -> Enable/Disable lighting

- Arrow key UP/DOWN -> Change the shadow
- Arrow key RIGHT/LEFT -> Rotate the object


## Implementação
A implementação desse projeto foi feito em python e tem como principal referência o tutorial:
> http://tfc.duke.free.fr/old/models/md2.htm

O tutorial acima implementa as funcionalidades em C++, e nele é possível encontrar melhores explicações e mais detalhes sobre cada uma das classes e funções definidas no projeto.
## Classes
Foram definidas algumas classes, e segue aqui uma breve explicação de cada uma:
## md2_t
Essa classe é responsável por definir propriedades do arquivo .md2 a partir da leitura de seu header. A partir do começo do arquivo, a cada 4 bits é definida uma propriedade, por isso os índices "pulam" de 4 em 4.
## vertex_t
Define, para cada vértice, suas coordenadas e também o index de sua normal.
## frame_t
Define propriedades de cada frame(scale,translate,name e os vértices respectivos). Mesma lógica que ocorre aqui ocorre na classe md2_t.
## anim_t
Define algumas propriedades de cada etapa da animação(primeira e última frame, além do fps)
## animState_t
Define propriedades da animação como um todo.

## Funções
Como são muitas funções, resolvi deixar comentado no código algumas explicações sobre cada uma delas (caso contrário esse markdown iria ficar bem extenso). Acesse o tutorial citado acima (não é de minha autoria) para explicações mais detalhadas. 

## Conclusão
Antes de finalizar esse texto, gostaria de deixar claro que a principal dificuladade encontrada aqui é realmente a manipulação dos dados e a leitura correta dos arquivos .md2 em PYTHON. O python possui tipos diferentes daqueles encontrados em C e C++, e por isso diversas conversões se fazem necessárias. Além disso, a implementação por classes como ocorre em C++ acaba por ser de certa forma mais limpa e "visível". Vale ressaltar uma frase que eu encontrei quando procurava maneiras de converter os tipos:
"Se você precisa dos tipos em C, provavelmente você deveria estar fazendo em C."

