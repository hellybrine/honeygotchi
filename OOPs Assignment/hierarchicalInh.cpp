#include <iostream>
using namespace std;

// Base class
class X {
public:
    int valueX;

    X() {
        valueX = 0;
    }

    void setX(int x) {
        valueX = x;
    }
};

// Derived classes (Hierarchical Inheritance)
class Y : public X {
public:
    int valueY;

    Y() {
        valueY = 0;
    }

    void setY(int y) {
        valueY = y;
    }
};

class Z : public X {
public:
    int valueZ;

    Z() {
        valueZ = 0;
    }

    void setZ(int z) {
        valueZ = z;
    }
};

int main() {
    Y objY;
    Z objZ;

    int x, y, z;
    cout << "Enter value for X (Y): ";
    cin >> x;
    cout << "Enter value for Y: ";
    cin >> y;
    cout << "Enter value for X (Z): ";
    cin >> z;

    objY.setY(y);
    objY.setX(x);  // Accessing the inherited function

    objZ.setZ(z);
    objZ.setX(x);  // Accessing the inherited function

    cout << "ValueX (Y): " << objY.valueX << endl;
    cout << "ValueY: " << objY.valueY << endl;

    cout << "ValueX (Z): " << objZ.valueX << endl;
    cout << "ValueZ: " << objZ.valueZ << endl;

    return 0;
}
