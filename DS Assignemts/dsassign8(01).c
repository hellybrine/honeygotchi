#include <stdio.h>
#include <stdlib.h>

struct TreeNode {
    int data;
    struct TreeNode* left;
    struct TreeNode* right;
};

struct TreeNode* createNode(int data) {
    struct TreeNode* newNode = (struct TreeNode*)malloc(sizeof(struct TreeNode));
    newNode->data = data;
    newNode->left = newNode->right = NULL;
    return newNode;
}

struct TreeNode* insert(struct TreeNode* root, int data) {
    if (root == NULL) {
        return createNode(data);
    }

    if (data < root->data) {
        root->left = insert(root->left, data);
    } else if (data > root->data) {
        root->right = insert(root->right, data);
    }

    return root;
}

struct TreeNode* findMinValueNode(struct TreeNode* node) {
    struct TreeNode* current = node;
    while (current->left != NULL) {
        current = current->left;
    }
    return current;
}

struct TreeNode* deleteNode(struct TreeNode* root, int data) {
    if (root == NULL) {
        return root;
    }

    if (data < root->data) {
        root->left = deleteNode(root->left, data);
    } else if (data > root->data) {
        root->right = deleteNode(root->right, data);
    } else {
        if (root->left == NULL) {
            struct TreeNode* temp = root->right;
            free(root);
            return temp;
        } else if (root->right == NULL) {
            struct TreeNode* temp = root->left;
            free(root);
            return temp;
        }

        struct TreeNode* temp = findMinValueNode(root->right);
        root->data = temp->data;
        root->right = deleteNode(root->right, temp->data);
    }

    return root;
}

void search(struct TreeNode* root, int key, struct TreeNode* parent) {
    if (root == NULL) {
        printf("Element not found in the BST.\n");
        return;
    }

    if (root->data == key) {
        printf("Element found in the BST.\n");
        printf("Parent: %d\n", parent ? parent->data : -1);
        printf("Left Child: %d\n", root->left ? root->left->data : -1);
        printf("Right Child: %d\n", root->right ? root->right->data : -1);
    } else if (key < root->data) {
        search(root->left, key, root);
    } else {
        search(root->right, key, root);
    }
}

void displayMenu() {
    printf("Binary Search Tree Menu:\n");
    printf("1. Add an element to the BST\n");
    printf("2. Delete element in the BST\n");
    printf("3. Search element in the BST\n");
    printf("4. Exit\n");
    printf("Enter your choice: ");
}

int main() {
    struct TreeNode* root = NULL;
    int choice, data;

    do {
        displayMenu();
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                printf("Enter the element to add: ");
                scanf("%d", &data);
                root = insert(root, data);
                break;
            case 2:
                printf("Enter the element to delete: ");
                scanf("%d", &data);
                root = deleteNode(root, data);
                break;
            case 3:
                printf("Enter the element to search: ");
                scanf("%d", &data);
                search(root, data, NULL);
                break;
            case 4:
                printf("Exiting the program.\n");
                break;
            default:
                printf("Invalid choice. Please try again.\n");
        }
    } while (choice != 4);

    return 0;
}