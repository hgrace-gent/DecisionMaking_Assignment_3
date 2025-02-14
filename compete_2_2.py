from profitModel import profitModels
from DataLoading import *
from InitialCostModel import costModel_complete
from Initial_Cost_Model_simple import costModel_PW_WU
from CostsCalc import Costs
from allocateCosts import allocateCost
import time
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt

class Competition:
    def __init__(self):
        self.demandData = demandFile('./given_data/demanddata.xlsx')
        self.demand = self.demandData.demand
        self.vCost = varCost('./given_data/variablecosts.xlsx')
        self.fCost = fixedCost('./given_data/fixedcosts.xlsx') 
        # demandData.printFile()

    def bestResponseUBFirst(self):
        
        profitList = [[0],[0]]
        counterList = [0,1]

        UB_profit, SE_profit,UB_profit_old,SE_profit_old = 0,0,0,0
        UB_warehouse, SE_warehouse = self.demandData.W[:2],self.demandData.W[2:]
        
        counter = 0
    
        print("We start the best response algorithm")

        # Initialize UB going first
        initial_UB = self.runModel(self.demand,UB_warehouse)
        UB_profit = initial_UB[0]
        new_Demand = initial_UB[2]
        profitList[0].append(UB_profit)
        profitList[1].append(SE_profit)

        while not ((UB_profit_old == UB_profit) and (SE_profit_old == SE_profit)):
            counter +=1
            print(f'---------------------Iteration: {counter} --------------------')

            ### SE makes it's plan based off of UB's allocation ##
            
            SE_attempt = self.runModel(new_Demand,SE_warehouse)
           

            SE_profit_old = SE_profit
            
            print("SE_Profit_old = ", SE_profit_old)

            SE_profit = SE_attempt[0]
           
            SE_strat = SE_attempt[1]
            new_Demand = SE_attempt[2]
            print(f'UB_Profit: {int(UB_profit)}, SE_Profit: {int(SE_profit)}')
            print(f'SE_Strategy {SE_strat[7:]}')
            print(f'demand after SE attempt {new_Demand[7:]}')
            # print(f'Fulfilled: \n {self.demandFulfillment(new_Demand)}')

           ## Now UB Turn to Respond ##
            UB_attempt = self.runModel(new_Demand,UB_warehouse) 
            UB_profit_old = UB_profit
            print("UB_Profit_old = ", UB_profit_old)
            
            UB_profit = UB_attempt[0]
            UB_strat = UB_attempt[1]
            new_Demand = UB_attempt[2]

            print(f'UB_Profit: {int(UB_profit)}, SE_Profit: {int(SE_profit)}')
            print(f'UB_Strategy {UB_strat[7:]}') 
            print(f'demand after UB attempt{new_Demand[7:]}')
            # print(f'Fulfilled: \n {self.demandFulfillment(new_Demand)}')

            profitList[0].append(UB_profit)
            profitList[1].append(SE_profit)
            counterList.append(counter)

            counter +=1

        self.plotProfits(profitList,counterList)

    def bestResponseSEFirst(self):
        
        profitList = [[0],[0]]
        counterList = [0,1]

        UB_profit, SE_profit,UB_profit_old,SE_profit_old = 0,0,0,0
        UB_warehouse, SE_warehouse = self.demandData.W[:2],self.demandData.W[2:]
        
        counter = 0
    
        print("We start the best response algorithm")

        # Initialize UB going first
        initial_SE = self.runModel(self.demand,SE_warehouse)
        UB_profit = initial_SE[0]
        new_Demand = initial_SE[2]
        profitList[0].append(UB_profit)
        profitList[1].append(SE_profit)

        while not ((UB_profit_old == UB_profit) and (SE_profit_old == SE_profit)):
            counter +=1
            print(f'---------------------Iteration: {counter} --------------------')

            UB_attempt = self.runModel(new_Demand,UB_warehouse) 
            
            UB_profit_old = UB_profit
            print("UB_Profit_old = ", UB_profit_old)
            
            UB_profit = UB_attempt[0]
            UB_strat = UB_attempt[1]
            new_Demand = UB_attempt[2]

            print(f'UB_Profit: {int(UB_profit)}, SE_Profit: {int(SE_profit)}')
            print(f'UB_Strategy {UB_strat[7:]}') 
            print(f'demand after UB attempt{new_Demand[7:]}')
            # print(f'Fulfilled: \n {self.demandFulfillment(new_Demand)}')

            SE_attempt = self.runModel(new_Demand,SE_warehouse)
           

            SE_profit_old = SE_profit
            
            print("SE_Profit_old = ", SE_profit_old)

            SE_profit = SE_attempt[0]
           
            SE_strat = SE_attempt[1]
            new_Demand = SE_attempt[2]
            print(f'UB_Profit: {int(UB_profit)}, SE_Profit: {int(SE_profit)}')
            print(f'SE_Strategy {SE_strat[7:]}')
            print(f'demand after SE attempt {new_Demand[7:]}')
            # print(f'Fulfilled: \n {self.demandFulfillment(new_Demand)}')


            profitList[0].append(UB_profit)
            profitList[1].append(SE_profit)
            counterList.append(counter)

            counter +=1

        self.plotProfits(profitList,counterList)   

    def plotProfits(self,profitList,counterList):
        plt.plot(counterList,profitList[0])
        plt.plot(counterList,profitList[1])
        plt.show()

    def runModel(self,givenDemand,warehouses):
        profitModel = profitModels(
                                        W = warehouses,  ## Removes the cross docks
                                        P = self.demandData.P,
                                        cap = self.demandData.capacity,
                                        U = self.demandData.U,   ## Change this to which universities you want, give it a list
                                        K = self.demandData.K,
                                        c = self.vCost.varCost,
                                        f = self.fCost.fixedCost,
                                        demand = givenDemand,
                                        supply = self.demandData.supply
                                    )
    
        model  = profitModel.model()
        profitModel.visualize_network(model,False)

        # newStrat = self.updateStrat(model)
        # newDemand = self.updateDemand(newStrat)

        newStrat = self.updateStrat(profitModel)
        newDemand = self.updateDemand(newStrat)

        profit = model.objVal

        return [profit,newStrat,newDemand,model]



        # print(demandData.demand)
   
    def updateStrat(self,model):
        newDemand = self.demand.copy()

        strat = np.zeros_like(newDemand)
        deliveringToU = []
        for w,u,k in model.x_wu_values.keys(): 
            index = [u,k]
            if index not in deliveringToU:
                deliveringToU.append([u,k])
            strat[u,k] = 1
        return strat

    def updateDemand(self,strat):
        
        strat_added_by_one = strat + 1

        newDemand = self.demand / strat_added_by_one

        return newDemand
    
    def demandFulfillment(self,newDemand):
        return (newDemand[8:])/(self.demand[8:])
    

    def visualize_results(self):
        G = nx.DiGraph()

        # Add nodes for printers, warehouses, and universities
        G.add_nodes_from(self.W, type="Warehouse", color="blue")
        G.add_nodes_from(self.P, type="Printer", color="green")
        G.add_nodes_from(self.U, type="University", color="red")

        # Dictionary to store aggregated flow values for edge labels
        edge_flows = {}

        # Add edges for flows from printers to warehouses
        for (p, w, k), flow in self.x_pw_values.items():
            if (p, w) not in edge_flows:
                edge_flows[(p, w)] = 0
            edge_flows[(p, w)] += flow
            G.add_edge(p, w, color="black")  # Add edge without weight for visualization

        # Add edges for flows from warehouses to universities
        for (w, u, k), flow in self.x_wu_values.items():
            if (w, u) not in edge_flows:
                edge_flows[(w, u)] = 0
            edge_flows[(w, u)] += flow
            G.add_edge(w, u, color="black")  # Add edge without weight for visualization

        # Define positions for nodes
        pos = {}
        for idx, p in enumerate(self.P):
            pos[p] = (0, idx)
        for idx, w in enumerate(self.W):
            pos[w] = (1, idx - len(self.W) // 2)
        for idx, u in enumerate(self.U):
            pos[u] = (2, idx - len(self.U) // 2)

        # Create edge labels based on aggregated flows
        edge_labels = {edge: f"{flow:.2f}" for edge, flow in edge_flows.items()}

        # Draw nodes
        colors = [data['color'] for _, data in G.nodes(data=True)]
        nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=500)

        # Draw edges
        edge_colors = [G[u][v]['color'] for u, v in G.edges]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors)

            # Draw labels
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_size=8,
            label_pos=0.65,  # Position of the label along the edge (0.5 is default)
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor="white", alpha=0.7),
        )

        plt.title("Optimization Results: Flow and Connections")
        plt.show()

