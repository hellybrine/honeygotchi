#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

struct TreeNode {
    char data;
    struct TreeNode* left;
    struct TreeNode* right;
};

struct TreeNode* createNode(char data) {
    struct TreeNode* newNode = (struct TreeNode*)malloc(sizeof(struct TreeNode));
    newNode->data = data;
    newNode->left = NULL;
    newNode->right = NULL;
    return newNode;
}

struct TreeNode* buildExpressionTree(char expression[], int* index) {
    struct TreeNode* newNode = NULL;

    while (expression[*index] != '\0') {
        char symbol = expression[(*index)++];
        if (isdigit(symbol) || isalpha(symbol)) {
            newNode = createNode(symbol);
        } else if (symbol == ' ') {
            // Ignore spaces
        } else {
            newNode = createNode(symbol);
            newNode->left = buildExpressionTree(expression, index);
            newNode->right = buildExpressionTree(expression, index);
        }

        return newNode;
    }
    return newNode;
}

void postfixTraversal(struct TreeNode* node) {
    if (node) {
        postfixTraversal(node->left);
        postfixTraversal(node->right);
        printf("%c", node->data);
    }
}

void prefixTraversal(struct TreeNode* node) {
    if (node) {
        printf("%c", node->data);
        prefixTraversal(node->left);
        prefixTraversal(node->right);
    }
}

int main() {
    char expression[] = "(8 * 4 + 6) / (2 - 1) + (7 * 3 - 5)";
    int index = 0;
    struct TreeNode* root = buildExpressionTree(expression, &index);

    printf("Postfix Expression: ");
    postfixTraversal(root);
    printf("\n");

    printf("Prefix Expression: ");
    prefixTraversal(root);
    printf("\n");

    return 0;
}
