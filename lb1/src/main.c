#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <sys/time.h>
#include <locale.h>

#define MAX_SIZE 250

typedef struct {
    int x, y, size, value;
} Square;

typedef struct {
    int boardSize;
    int squareCount;
    int** board;
    Square squares[40];
} Board;

Board* createBoard(int size) {
    Board* newBoard = (Board*) malloc(sizeof(Board));
    newBoard->boardSize = size;
    newBoard->squareCount = 0;

    newBoard->board = (int**) malloc(size * sizeof(int*));
    for (int i = 0; i < size; i++) {
        newBoard->board[i] = (int*) calloc(size, sizeof(int));
    }

    return newBoard;
}

void freeBoard(Board* board) {
    for (int i = 0; i < board->boardSize; i++) {
        free(board->board[i]);
    }

    free(board->board);
    free(board);
}

Board* createBoardCopy(Board* origBoard) {
    Board* newBoard = createBoard(origBoard->boardSize);
    newBoard->squareCount = origBoard->squareCount;

    for (int y = 0; y < origBoard->boardSize; y++) {
        for (int x = 0; x < origBoard->boardSize; x++) {
            newBoard->board[y][x] = origBoard->board[y][x];
        }
    }

    for (int i = 0; i < origBoard->squareCount; i++) {
        newBoard->squares[i] = origBoard->squares[i];
    }

    return newBoard;
}

void copyBoardValue(Board* origBoard, Board* destBoard) {
    destBoard->squareCount = origBoard->squareCount;
    destBoard->boardSize = origBoard->boardSize;

    for (int y = 0; y < origBoard->boardSize; y++) {
        for (int x = 0; x < origBoard->boardSize; x++) {
            destBoard->board[y][x] = origBoard->board[y][x];
        }
    }

    for (int i = 0; i < origBoard->squareCount; i++) {
        destBoard->squares[i] = origBoard->squares[i];
    }
}

bool checkFilled(Board* board) {
    for (int y = 0; y < board->boardSize; y++) {
        for (int x = 0; x < board->boardSize; x++) {
            if (board->board[y][x] == 0) {
                return false;
            }
        }
    }
    return true;
}

void findEmptyCell(Board* board, int* x, int* y) {
    for (int Y = 0; Y < board->boardSize; Y++) {
        for (int X = 0; X < board->boardSize; X++) {
            if (board->board[Y][X] == 0) {
                *x = X; *y = Y;
                return;
            }
        }
    }

    *x = -1; *y = -1;
}

bool checkSpace(Board* board, Square square) {
    if (square.x + square.size > board->boardSize || square.y + square.size > board->boardSize) {
        return false;
    }

    for (int y = 0; y < square.size; y++) {
        for (int x = 0; x < square.size; x++) {
            if (board->board[y + square.y][x + square.x] > 0) {
                return false;
            }
        }
    }

    return true;
}

void placeSquare(Board* board, Square square) {
    wprintf(L"\t -> Размещаем квадрат размером %dx%d на позицию (%d, %d).\n", square.size, square.size, square.x, square.y);
    for (int y = 0; y < square.size; y++) {
        for (int x = 0; x < square.size; x++) {
            board->board[y + square.y][x + square.x] = board->squareCount + 1;
        }
    }

    board->squares[board->squareCount++] = square;
}

void printBoard(Board* board) {
    wprintf(L"\t");
    for (int y = 0; y < board->boardSize; y++) {
        for (int x = 0; x < board->boardSize; x++) {
            wprintf(L"%d ", board->board[y][x]);
        }
        if (y < board->boardSize - 1) wprintf(L"\n\t");
        else wprintf(L"\n");
    }
}

void printSquares(Board* board) {
    wprintf(L"%d\n", board->squareCount);
    for (int i = 0; i < board->squareCount; i++) {
        wprintf(L"%d %d %d\n", board->squares[i].x, board->squares[i].y, board->squares[i].size);
    }
}

void placeSquaresForPrime(Board* board) {
    wprintf(L"Для доски, размер которой - простое число, заранее известно оптимальное расположение первых трех квадратов:\n");

    Square s1 = {0, 0, (board->boardSize + 1) / 2};
    Square s2 = {0, (board->boardSize + 1) / 2, (board->boardSize - 1) / 2};
    Square s3 = {(board->boardSize + 1) / 2, 0, (board->boardSize - 1) / 2};

    placeSquare(board, s1);
    placeSquare(board, s2);
    placeSquare(board, s3);

    printBoard(board);
}

void placeSquaresForEven(Board* board) {
    wprintf(L"Для доски, размер которой - четное число, заранее известно оптимальное расположение первых трех квадратов:\n");

    Square s1 = {0, 0, board->boardSize / 2};
    Square s3 = {0, board->boardSize / 2, board->boardSize / 2};
    Square s2 = {board->boardSize / 2, 0, board->boardSize / 2};
    Square s4 = {board->boardSize / 2, board->boardSize / 2, board->boardSize/ 2};

    placeSquare(board, s1);
    placeSquare(board, s2);
    placeSquare(board, s3);
    placeSquare(board, s4);

    printBoard(board);
}

void placeSquaresForThree(Board* board) {
    wprintf(L"Для доски, размер которой делится на 3, заранее известно оптимальное расположение первых трех квадратов:\n");
    int size = board->boardSize - board->boardSize / 3;
    Square s1 = {0, 0, size};
    Square s3 = {0, size, board->boardSize / 3};
    Square s2 = {size, 0, board->boardSize / 3};

    placeSquare(board, s1);
    placeSquare(board, s2);
    placeSquare(board, s3);

    wprintf(L"Получившееся заполнение доски:\n");
    printBoard(board);
}

void backtracking(Board* board) {
    Board* allBoards[MAX_SIZE];
    int x, y;
    int allBoardsCount = 0;
    int operationCount = 0;
    allBoards[allBoardsCount++] = board;

    while (allBoardsCount > 0) {
        findEmptyCell(allBoards[0], &x, &y);
        Board* currentBoard = createBoardCopy(allBoards[0]);

        wprintf(L"---------------------\nВозьмем первый в очереди вариант и попробуем разместить на нем квадраты всех доступных размеров:\n");
        printBoard(currentBoard);
        wprintf(L"Найденная пустая клетка: (%d, %d).\n", x, y);
        wprintf(L"Проверим какие квадраты можно в ней разместить:\n");

        for (int size = board->boardSize - 1; size > 0; size--) { 
            Square square = {x, y, size, currentBoard->squareCount};
            Board* newBoard = createBoardCopy(currentBoard);
            operationCount++;

            if (checkSpace(newBoard, square)) {
                placeSquare(newBoard, square);

                wprintf(L"Получившееся заполнение доски:\n");
                printBoard(newBoard);

                if (allBoardsCount < MAX_SIZE) {
                    allBoards[allBoardsCount++] = createBoardCopy(newBoard);
                }

                if (checkFilled(newBoard)) {
                    wprintf(L"---------------------\nЗаполнение доски размером %d потребовало %d операций.\n", board->boardSize, operationCount);
                    copyBoardValue(newBoard, board);
                    for (int i = 0; i < allBoardsCount; i++) {
                        freeBoard(allBoards[i]);
                    }
                    freeBoard(newBoard);
                    freeBoard(currentBoard);
                    return;
                }
            }

            freeBoard(newBoard);
        }
    
        freeBoard(currentBoard);
        wprintf(L"Для данного варианта были рассмотрены размещения всех возможных размеров квадратов, удаляем его из очереди.\n");
        for (int i = 0; i < allBoardsCount - 1; i++) {
            allBoards[i] = allBoards[i + 1];
        }
        allBoardsCount--;
    }
}

int main() {
    setlocale(LC_ALL, "Russian");
    int size;
    scanf("%d", &size);
    if (size >= 2 && size <= 40) {
        Board* board = createBoard(size);
        struct timeval stop, start;

        gettimeofday(&start, NULL);

        if (size % 2 == 0) {
            placeSquaresForEven(board);
        }

        else if (size % 3 == 0) {
            placeSquaresForThree(board);
            backtracking(board);
        }

        else {
            placeSquaresForPrime(board);
            backtracking(board);
        }

        gettimeofday(&stop, NULL);

        double seconds = (stop.tv_sec - start.tv_sec) + (stop.tv_usec - start.tv_usec) / 1000000.0;
        wprintf(L"Заполнение доски размером %d заняло %.6f секунд.\n", board->boardSize, seconds);

        wprintf(L"Итоговый вариант заполнения доски:\n");
        printBoard(board);
        freeBoard(board);
    }
    return 0;
}