#include<iostream>
using namespace std;

struct Process {
    int id;
    int arrivalTime;
    int burstTime;
};

void findWaitingTime(Process processes[], int n, int wt[]) {
    wt[0] = 0;
    for (int i = 1; i < n; i++) {
        wt[i] = processes[i - 1].burstTime + wt[i - 1];
    }
}

void findTurnAroundTime(Process processes[], int n, int wt[], int tat[]) {
    for (int i = 0; i < n; i++) {
        tat[i] = processes[i].burstTime + wt[i];
    }
}

void findAverageTime(Process processes[], int n) {
    int wt[n], tat[n], total_wt = 0, total_tat = 0;
    findWaitingTime(processes, n, wt);
    findTurnAroundTime(processes, n, wt, tat);
    cout << "Processes  " << " Arrival time  " << " Burst time  " << " Waiting time  " << " Turn around time\n";
    for (int i = 0; i < n; i++) {
        total_wt += wt[i];
        total_tat += tat[i];
        cout << "   " << processes[i].id << "\t\t" << processes[i].arrivalTime << "\t\t" << processes[i].burstTime << "\t\t" << wt[i] << "\t\t  " << tat[i] << endl;
    }
    cout << "Average waiting time = " << (float)total_wt / (float)n;
    cout << "\nAverage turn around time = " << (float)total_tat / (float)n;
}

int main() {
    int n;
    cout << "Enter the number of processes: ";
    cin >> n;
    
    Process processes[n];
    for (int i = 0; i < n; i++) {
        cout << "Enter arrival time and burst time for process " << i + 1 << ": ";
        cin >> processes[i].arrivalTime >> processes[i].burstTime;
        processes[i].id = i + 1;
    }

    findAverageTime(processes, n);
    return 0;
}
