#!/anaconda3/bin/python3
# -*- coding: utf-8 -*-
"""
Script to test NAPS functionality
Run with a single argument, the path to the NAPS directory
eg "python NAPS_test.py /Users/aph516/GitHub/NAPS/"

@author: aph516
"""

import numpy as np
import pandas as pd
from subprocess import run, Popen, PIPE
from pathlib import Path
import argparse
from plotnine import *

# Set the path to the NAPS directory
parser = argparse.ArgumentParser(
        description="Test script for NAPS (NMR Assignments from Predicted Shifts)")
parser.add_argument("NAPS_path", help="Path to the top-level NAPS directory.")
parser.add_argument("-p", "--python_cmd", default="python")
parser.add_argument("--assign", action="store_true", help="Do NAPS assignment for selected tests.")
parser.add_argument("--analyse", action="store_true", help="Analyse results for selected tests.")
parser.add_argument("-N", default=None, help="Limit to first N datasets.")
parser.add_argument("-t", "--test", nargs="+", default="all", 
                    help="Specify a particular test to run.")

if True:
    args = parser.parse_args()
else:
    #args = parser.parse_args(("C:/Users/kheyam/Documents/GitHub/NAPS/",
    args = parser.parse_args(("/Users/aph516/GitHub/NAPS/",
                              "-t","all",
                              "--assign",
                              "--analyse",
                              "--ID_start","A003",
                              "--ID_end","A069"))

path = Path(args.NAPS_path)
#path = Path("/Users/aph516/GitHub/NAPS/")
#path = Path("C:/Users/kheyam/Documents/GitHub/NAPS/")

# Import metadata on the test datasets
testset_df = pd.read_table(path/"data/testset/testset.txt", header=None, 
                           names=["ID","PDB","BMRB","Resolution","Length"])
testset_df["obs_file"] = [path/x for x in "data/testset/simplified_BMRB/"+testset_df["BMRB"].astype(str)+".txt"]
testset_df["preds_file"] = [path/x for x in "data/testset/shiftx2_results/"+testset_df["ID"]+"_"+testset_df["PDB"]+".cs"]
testset_df["out_name"] = testset_df["ID"]+"_"+testset_df["BMRB"].astype(str)
testset_df.index = testset_df["ID"]

# Define some lists of ID's with particular characteristics
id_all = testset_df["ID"].tolist()  # All ID's

    # Only ID's with info for C, CA and CB (not necessarily complete)
id_all_carbons = [
        'A002', 'A003', 'A004', 'A005', 'A006', 'A008', 'A009', 'A010', 'A011',
        'A012', 'A013', 'A014', 'A015', 'A016', 'A017', 'A018', 'A019', 'A020',
        'A021', 'A023', 'A025', 'A026', 'A027', 'A028', 'A029', 'A033', 'A035',
        'A036', 'A037', 'A039', 'A043', 'A044', 'A045', 'A049', 'A050', 'A051',
        'A053', 'A059', 'A061', 'A062', 'A066', 'A067', 'A069']

# Limit how many datasets are assigned/analysed
if args.N is not None:
    id_all = id_all[0:args.N]
    id_all_carbons = id_all_carbons[0:args.N]
#%%

def check_assignment_accuracy(data_dir, ranks=[1], prefix="", ID_list=id_all):
    """Function to check assignment accuracy
    """
    # Nb. make sure data_dir ends with a forward slash

    assigns = None
    for i in ID_list:
        tmp_all = pd.read_csv(
                data_dir/(prefix+testset_df.loc[i, "out_name"]+".txt"), 
                sep="\t", index_col=False)
        tmp_all["ID"] = i
        
        # Cysteines in disulphide bridges are often named B in this dataset. 
        # We don't need to know this, so change to C
        mask = tmp_all["Res_type"]=="B"
        tmp_all.loc[mask,"Res_type"] = "C"
        tmp_all.loc[mask, "Res_name"] = (tmp_all.loc[mask,"Res_name"].
                   str.replace("B","C"))
        
        # Restrict to just the ranks being considered (ie. when output contains 
        # alternative assignments)
        if "Rank" not in tmp_all.columns:
            tmp_all["Rank"] = 1
            tmp_all["Rel_prob"] = 0
        
        tmp = tmp_all.loc[tmp_all["Rank"].isin(ranks),:].copy()
        tmp["Rank"] = tmp["Rank"].astype(str)
        if "Max_mismatch_prev" in tmp.columns:
            tmp = tmp[["ID","Res_N","Res_type","Res_name","SS_name","Log_prob",
                       "Rank","Rel_prob","Dummy_SS","Dummy_res",
                       "Max_mismatch_prev","Max_mismatch_next",
                       "Num_good_links_prev","Num_good_links_next"]]
        else:
            tmp = tmp[["ID","Res_N","Res_type","Res_name","SS_name","Log_prob",
                       "Rank","Rel_prob","Dummy_SS","Dummy_res"]]
       
        # Convert Res_N column to integer
        tmp.loc[:,"Res_N"] = tmp.loc[:,"Res_N"].fillna(-999)
        tmp.loc[:,"Res_N"] = tmp.loc[:,"Res_N"].astype(int)
        # Cysteines in disulphide bridges are often named B in this dataset. 
        # We don't need to know this, so change to C
        mask = tmp["Res_type"]=="B"
        tmp.loc[mask,"Res_type"] = "C"
        tmp.loc[mask, "Res_name"] = tmp.loc[mask,"Res_name"].str.replace("B","C")
        # Add a column saying whether a match exists for the spin system 
        # (ie whether a correct assignment is possible)
        tmp["SS_in_pred"] = tmp["SS_name"].isin(tmp_all["Res_name"])
        tmp["Pred_in_SS"] = tmp["Res_name"].isin(tmp_all["SS_name"])
        
        if assigns is None:
            assigns = tmp
        else:
            assigns = pd.concat([assigns, tmp], ignore_index=True)
    
    # Determine which spin systems were correctly assigned
    assigns["Correct"] = False
    assigns["Status"] = ""
    
    mask = assigns["SS_in_pred"] & ~assigns["Dummy_SS"]
    assigns.loc[mask & (assigns["SS_name"]==assigns["Res_name"]), 
                "Correct"] = True
    assigns.loc[mask & (assigns["SS_name"]==assigns["Res_name"]), 
                "Status"] = "Correctly assigned"
    assigns.loc[mask & (assigns["SS_name"]!=assigns["Res_name"]), 
                "Status"] = "Misassigned"
    assigns.loc[mask & assigns["Dummy_res"], "Status"] = "Wrongly unassigned"
    
    mask = ~assigns["SS_in_pred"] & ~assigns["Dummy_SS"]
    assigns.loc[mask & (assigns["SS_name"]!=assigns["Res_name"]), 
                "Status"] = "Wrongly assigned"
    assigns.loc[mask & assigns["Dummy_res"], "Correct"] = True
    assigns.loc[mask & assigns["Dummy_res"], "Status"] = "Correctly unassigned"
    
    assigns.loc[assigns["Dummy_SS"], "Status"] = "Dummy SS"
    assigns.loc[:,"Status"] = assigns["Status"].astype("category")
    
    # Make the summary dataframe
    ID_unique = assigns["ID"].unique()
    Rank_unique = assigns["Rank"].unique()
    
    # We want:
    # ID1 Rank1
    # ID1 Rank2
    # ...
    # ID1 RankN
    # ID2 Rank1
    # ...
    # ID2 RankN
    # ID3 Rank1
    # ...
    Rank_list = list(Rank_unique)*len(ID_unique)
    ID_list2 = list(ID_unique.repeat(len(Rank_unique)))
    status_list=["Correctly assigned","Correctly unassigned","Dummy SS",
                 "Misassigned","Wrongly assigned","Wrongly unassigned"]
    
    summary = pd.DataFrame({"ID":ID_list2, "Rank":Rank_list}, 
                           columns=["ID", "Rank"]+status_list)

    for i in summary.index:
        tmp = assigns.loc[(assigns["ID"] == summary.loc[i, "ID"]) &
                          (assigns["Rank"] == summary.loc[i, "Rank"]),:]
        for status in status_list:
            summary.loc[i, status] = sum(tmp["Status"]==status)
                
    #summary = summary.loc[:,status_list].fillna(0).astype(int)
    summary["N"] = summary.loc[:,status_list].apply(sum, axis=1)
    summary["N_SS"] = summary["N"] - summary["Dummy SS"]
    
    
    # Add rows with sums for all ranks
    for r in Rank_unique:
        sum_row = (summary.loc[summary["Rank"]==r,:].sum(axis=0).
                       to_frame("Sum").transpose())
        sum_row["ID"] = "Sum"
        sum_row["Rank"] = r
        summary = pd.concat([sum_row, summary], sort=False, ignore_index=True)

    summary["Pc_correct"] = (summary["Correctly assigned"]+
                             summary["Correctly unassigned"]) / summary["N_SS"]
    
    return([assigns, summary])

#%% Test all proteins in the using most basic settings
if args.assign and ("basic" in args.test or "all" in args.test):
    for i in id_all:
        print((path/("output/testset/"+testset_df.loc[i, "out_name"]+".txt")).as_posix())
        cmd = [args.python_cmd, (path/"python/NAPS.py").as_posix(),
                testset_df.loc[i, "obs_file"].as_posix(), 
                testset_df.loc[i, "preds_file"].as_posix(),
                (path/("output/basic/"+testset_df.loc[i, "out_name"]+".txt")).as_posix(),
                "--shift_type", "test",
                "--pred_type", "shiftx2",
                "-c", (path/"config/config_plot.txt").as_posix(),
                "-l", (path/("output/basic/"+testset_df.loc[i, "out_name"]+".log")).as_posix(),
                "--plot_file", (path/("plots/basic/"+testset_df.loc[i, "out_name"]+"_strips.pdf")).as_posix()]
        run(cmd)

if args.analyse and ("basic" in args.test or "all" in args.test):        
    assigns_std, summary_std = check_assignment_accuracy(path/"output/basic/", ID_list=id_all)
    summary_std.to_csv(path/"output/basic_summary.txt", sep="\t", float_format="%.3f")
    
    plt = ggplot(data=assigns_std) + geom_bar(aes(x="ID", fill="Status"), position=position_fill(reverse=True))
    plt = plt + geom_text(aes(x="summary_std.index", label="Pc_correct"), y=0.1, format_string="{:.0%}", data=summary_std, angle=90)
    plt = plt + theme(axis_text_x=element_text(rotation=90, hjust=1))
    plt.save(path/"plots/basic_summary.pdf", height=210, width=297, units="mm", limitsize=False)

#%% Test effect of correcting the predicted shifts
if args.assign and ("pred_correction" in args.test or "all" in args.test):
    for i in id_all:
        print(testset_df.loc[i, "out_name"])    
        cmd = [args.python_cmd, (path/"python/NAPS.py").as_posix(),
                testset_df.loc[i, "obs_file"].as_posix(),
                testset_df.loc[i, "preds_file"].as_posix(), 
                (path/("output/pred_correction/"+testset_df.loc[i, "out_name"]+".txt")).as_posix(),
                "--shift_type", "test",
                "--pred_type", "shiftx2",
                "-c", (path/"config/config_pred_correction.txt").as_posix(),
                "-l", (path/("output/pred_correction/"+testset_df.loc[i, "out_name"]+".log")).as_posix()]
        run(cmd)

if args.analyse and ("pred_correction" in args.test or "all" in args.test):        
    assigns_dc, summary_dc = check_assignment_accuracy(path/"output/pred_correction/", ID_list=id_all)
    summary_dc.to_csv(path/"output/pred_correction_summary.txt", sep="\t", float_format="%.3f")
    
    plt = ggplot(data=assigns_dc) + geom_bar(aes(x="ID", fill="Status"), position=position_fill(reverse=True))
    plt = plt + geom_text(aes(x="summary_dc.index", label="Pc_correct"), y=0.1, format_string="{:.0%}", data=summary_std, angle=90)
    plt = plt + theme(axis_text_x=element_text(rotation=90, hjust=1))
    plt.save(path/"plots/pred_correction_summary.pdf", height=210, width=297, units="mm")


#%% Test effect of accounting for correlated errors
if args.assign and ("delta_correlation" in args.test or "all" in args.test):
    for i in id_all:
        print(testset_df.loc[i, "out_name"])    
        cmd = [args.python_cmd, (path/"python/NAPS.py").as_posix(),
                testset_df.loc[i, "obs_file"].as_posix(),
                testset_df.loc[i, "preds_file"].as_posix(), 
                (path/("output/delta_correlation/"+testset_df.loc[i, "out_name"]+".txt")).as_posix(),
                "--shift_type", "test",
                "--pred_type", "shiftx2",
                "-c", (path/"config/config_delta_corr.txt").as_posix(),
                "-l", (path/("output/delta_correlation/"+testset_df.loc[i, "out_name"]+".log")).as_posix()]
        run(cmd)

if args.analyse and ("delta_correlation" in args.test or "all" in args.test):        
    assigns_dc, summary_dc = check_assignment_accuracy(path/"output/delta_correlation/", ID_list=id_all)
    summary_dc.to_csv(path/"output/delta_correlation_summary.txt", sep="\t", float_format="%.3f")
    
    plt = ggplot(data=assigns_dc) + geom_bar(aes(x="ID", fill="Status"), position=position_fill(reverse=True))
    plt = plt + geom_text(aes(x="summary_dc.index", label="Pc_correct"), y=0.1, format_string="{:.0%}", data=summary_std, angle=90)
    plt = plt + theme(axis_text_x=element_text(rotation=90, hjust=1))
    plt.save(path/"plots/delta_correlation_summary.pdf", height=210, width=297, units="mm")

#%% Test effect of accounting for correlated errors *and* correcting the predicted shifts
if args.assign and ("delta_correlation2" in args.test or "all" in args.test):
    for i in id_all:
        print(testset_df.loc[i, "out_name"])    
        cmd = [args.python_cmd, (path/"python/NAPS.py").as_posix(),
                testset_df.loc[i, "obs_file"].as_posix(),
                testset_df.loc[i, "preds_file"].as_posix(), 
                (path/("output/delta_correlation2/"+testset_df.loc[i, "out_name"]+".txt")).as_posix(),
                "--shift_type", "test",
                "--pred_type", "shiftx2",
                "-c", (path/"config/config_delta_corr2.txt").as_posix(),
                "-l", (path/("output/delta_correlation2/"+testset_df.loc[i, "out_name"]+".log")).as_posix()]
        run(cmd)

if args.analyse and ("delta_correlation2" in args.test or "all" in args.test):        
    assigns_dc, summary_dc = check_assignment_accuracy(path/"output/delta_correlation2/", ID_list=id_all)
    summary_dc.to_csv(path/"output/delta_correlation2_summary.txt", sep="\t", float_format="%.3f")
    
    plt = ggplot(data=assigns_dc) + geom_bar(aes(x="ID", fill="Status"), position=position_fill(reverse=True))
    plt = plt + geom_text(aes(x="summary_dc.index", label="Pc_correct"), y=0.1, format_string="{:.0%}", data=summary_std, angle=90)
    plt = plt + theme(axis_text_x=element_text(rotation=90, hjust=1))
    plt.save(path/"plots/delta_correlation2_summary.pdf", height=210, width=297, units="mm")

#%% Test effect of including HADAMAC amino acid type information
if args.assign and ("hadamac" in args.test or "all" in args.test):
    for i in id_all:
        print(testset_df.loc[i, "out_name"])    
        cmd = [args.python_cmd, (path/"python/NAPS.py").as_posix(),
                testset_df.loc[i, "obs_file"].as_posix(),
                testset_df.loc[i, "preds_file"].as_posix(), 
                (path/("output/hadamac/"+testset_df.loc[i, "out_name"]+".txt")).as_posix(),
                "--shift_type", "test",
                "--pred_type", "shiftx2",
                "--test_aa_classes", "ACDEFGHIKLMNPQRSTVWY;G,S,T,AVI,DN,FHYWC,REKPQML",
                "-c", (path/"config/config_hadamac.txt").as_posix(),
                "-l", (path/("output/hadamac/"+testset_df.loc[i, "out_name"]+".log")).as_posix()]
        run(cmd)

if args.analyse and ("hadamac" in args.test or "all" in args.test):        
    assigns_dc, summary_dc = check_assignment_accuracy(path/"output/hadamac/", ID_list=id_all)
    summary_dc.to_csv(path/"output/hadamac_summary.txt", sep="\t", float_format="%.3f")
    
    plt = ggplot(data=assigns_dc) + geom_bar(aes(x="ID", fill="Status"), position=position_fill(reverse=True))
    plt = plt + geom_text(aes(x="summary_dc.index", label="Pc_correct"), y=0.1, format_string="{:.0%}", data=summary_std, angle=90)
    plt = plt + theme(axis_text_x=element_text(rotation=90, hjust=1))
    plt.save(path/"plots/hadamac_summary.pdf", height=210, width=297, units="mm")


#%% Test alternative assignments
if args.assign and ("alt_assignments" in args.test or "all" in args.test):
    for i in id_all_carbons:
        print(testset_df.loc[i, "out_name"])    
        cmd = [args.python_cmd, (path/"python/NAPS.py").as_posix(),
                testset_df.loc[i, "obs_file"].as_posix(), 
                testset_df.loc[i, "preds_file"].as_posix(), 
                (path/("output/alt_assign/"+testset_df.loc[i, "out_name"]+".txt")).as_posix(), 
                "--shift_type", "test",
                "--pred_type", "shiftx2",
                "-c", (path/"config/config_alt_assign.txt").as_posix(),
                "-l", (path/("output/alt_assign/"+testset_df.loc[i, "out_name"]+".log")).as_posix()]
        run(cmd)

if args.analyse and ("alt_assignments" in args.test or "all" in args.test):        
    assigns_alt, summary_alt = check_assignment_accuracy(path/"output/alt_assign/", ranks=[1,2,3], ID_list=id_all_carbons)
    assigns_alt = assigns_alt.sort_values(by=["ID", "SS_name", "Rank"])
    
    assigns_alt.to_csv(path/"output/alt_assign_all.txt", sep="\t", float_format="%.3f")
    summary_alt.to_csv(path/"output/alt_assign_summary.txt", sep="\t", float_format="%.3f")

    plt = ggplot(data=assigns_alt) + geom_bar(aes(x="ID", fill="Status"), position=position_fill(reverse=True)) + facet_grid("Rank ~ .")
    plt = plt + theme(axis_text_x = element_text(angle=90))
    plt.save(path/"plots/alt_assign_summary.pdf", height=210, width=297, units="mm")
    
    tmp = summary_alt
    tmp["Pc_correct"] = tmp["Pc_correct"].astype(float)
    rank_cat = pd.api.types.CategoricalDtype(categories=["3","2","1"], ordered=True)
    tmp["Rank"] = tmp["Rank"].astype(str).astype(rank_cat)
    plt = ggplot(data=tmp) + geom_bar(aes(x="ID", y="Pc_correct", fill="Rank"), stat="identity")
    plt = plt + theme(axis_text_x=element_text(rotation=90, hjust=0.5))
    plt = plt + scale_y_continuous(breaks=np.linspace(0,1,11))
    plt.save(path/"plots/alt_assign_correct.pdf", height=210, width=297, units="mm")
    
#%% Test alternative assignments with reduced atom types
if args.assign and ("alt_hnco" in args.test or "all" in args.test):
    for i in id_all_carbons:
        print(testset_df.loc[i, "out_name"])    
        cmd = [args.python_cmd, (path/"python/NAPS.py").as_posix(),
                testset_df.loc[i, "obs_file"].as_posix(), 
                testset_df.loc[i, "preds_file"].as_posix(), 
                (path/("output/alt_hnco/"+testset_df.loc[i, "out_name"]+".txt")).as_posix(), 
                "--shift_type", "test",
                "--pred_type", "shiftx2", 
                "-c", (path/"config/config_alt_hnco.txt").as_posix(),
                "-l", (path/("output/alt_hnco/"+testset_df.loc[i, "out_name"]+".log")).as_posix()]
        run(cmd)
        
if args.analyse and ("alt_hnco" in args.test or "all" in args.test):
    assigns_alt_hnco, summary_alt_hnco = check_assignment_accuracy(path/"output/alt_hnco/", ranks=[1,2,3], ID_list=id_all_carbons)
    assigns_alt_hnco = assigns_alt_hnco.sort_values(by=["ID", "SS_name", "Rank"])
    
    assigns_alt_hnco.to_csv(path/"output/alt_hnco_all.txt", sep="\t", float_format="%.3f")
    summary_alt_hnco.to_csv(path/"output/alt_hnco_summary.txt", sep="\t", float_format="%.3f")

    plt = ggplot(data=assigns_alt_hnco) + geom_bar(aes(x="ID", fill="Status"), position=position_fill(reverse=True)) + facet_grid("Rank ~ .")
    plt = plt + theme(axis_text_x = element_text(angle=90))
    plt.save(path/"plots/alt_hnco_summary.pdf", height=210, width=297, units="mm")
    
    tmp = summary_alt_hnco
    tmp["Pc_correct"] = tmp["Pc_correct"].astype(float)
    rank_cat = pd.api.types.CategoricalDtype(categories=["3","2","1"], ordered=True)
    tmp["Rank"] = tmp["Rank"].astype(str).astype(rank_cat)
    plt = ggplot(data=tmp) + geom_bar(aes(x="ID", y="Pc_correct", fill="Rank"), stat="identity")
    plt = plt + theme(axis_text_x=element_text(rotation=90, hjust=0.5))
    plt = plt + scale_y_continuous(breaks=np.linspace(0,1,11))
    plt.save(path/"plots/alt_hnco_correct.pdf", height=210, width=297, units="mm")

if args.assign and ("alt_hnco_hncacb" in args.test or "all" in args.test):        
    for i in id_all_carbons:
        print(testset_df.loc[i, "out_name"])    
        cmd = [args.python_cmd, (path/"python/NAPS.py").as_posix(),
                testset_df.loc[i, "obs_file"].as_posix(), 
                testset_df.loc[i, "preds_file"].as_posix(), 
                (path/("output/alt_hnco_hncacb/"+testset_df.loc[i, "out_name"]+".txt")).as_posix(), 
                "--shift_type", "test",
                "--pred_type", "shiftx2", 
                "-c", (path/"config/config_alt_hnco_hncacb.txt").as_posix(),
                "-l", (path/("output/alt_hnco_hncacb/"+testset_df.loc[i, "out_name"]+".log")).as_posix()]
        run(cmd)
        
if args.analyse and ("alt_hnco_hncacb" in args.test or "all" in args.test):        
    assigns_alt_hnco_hncacb, summary_alt_hnco_hncacb = check_assignment_accuracy(path/"output/alt_hnco_hncacb/", ranks=[1,2,3], ID_list=id_all_carbons)
    assigns_alt_hnco_hncacb = assigns_alt_hnco_hncacb.sort_values(by=["ID", "SS_name", "Rank"])
    
    assigns_alt_hnco_hncacb.to_csv(path/"output/alt_hnco_hncacb_all.txt", sep="\t", float_format="%.3f")
    summary_alt_hnco_hncacb.to_csv(path/"output/alt_hnco_hncacb_summary.txt", sep="\t", float_format="%.3f")

    plt = ggplot(data=assigns_alt_hnco_hncacb) + geom_bar(aes(x="ID", fill="Status"), position=position_fill(reverse=True)) + facet_grid("Rank ~ .")
    plt = plt + theme(axis_text_x = element_text(angle=90))
    plt.save(path/"plots/alt_hnco_hncacb_summary.pdf", height=210, width=297, units="mm")
    
    tmp = summary_alt_hnco_hncacb
    tmp["Pc_correct"] = tmp["Pc_correct"].astype(float)
    rank_cat = pd.api.types.CategoricalDtype(categories=["3","2","1"], ordered=True)
    tmp["Rank"] = tmp["Rank"].astype(str).astype(rank_cat)
    plt = ggplot(data=tmp) + geom_bar(aes(x="ID", y="Pc_correct", fill="Rank"), stat="identity")
    plt = plt + theme(axis_text_x=element_text(rotation=90, hjust=0.5))
    plt = plt + scale_y_continuous(breaks=np.linspace(0,1,11))
    plt.save(path/"plots/alt_hnco_hncacb_correct.pdf", height=210, width=297, units="mm")

if args.assign and ("alt_ca_co" in args.test or "all" in args.test):    
    for i in id_all_carbons:
        print(testset_df.loc[i, "out_name"])    
        cmd = [args.python_cmd, (path/"python/NAPS.py").as_posix(),
                testset_df.loc[i, "obs_file"].as_posix(), 
                testset_df.loc[i, "preds_file"].as_posix(), 
                (path/("output/alt_ca_co/"+testset_df.loc[i, "out_name"]+".txt")).as_posix(), 
                "--shift_type", "test",
                "--pred_type", "shiftx2", 
                "-c", (path/"config/config_alt_ca_co.txt").as_posix(),
                "-l", (path/("output/alt_ca_co/"+testset_df.loc[i, "out_name"]+".log")).as_posix()]
        run(cmd)

if args.analyse and ("alt_ca_co" in args.test or "all" in args.test):            
    assigns_alt_ca_co, summary_alt_ca_co = check_assignment_accuracy(path/"output/alt_ca_co/", ranks=[1,2,3], id_all = id_all[0:args.N])
    assigns_alt_ca_co = assigns_alt_ca_co.sort_values(by=["ID", "SS_name", "Rank"])
    
    assigns_alt_ca_co.to_csv(path/"output/alt_ca_co_all.txt", sep="\t", float_format="%.3f")
    summary_alt_ca_co.to_csv(path/"output/alt_ca_co_summary.txt", sep="\t", float_format="%.3f")

    plt = ggplot(data=assigns_alt_ca_co) + geom_bar(aes(x="ID", fill="Status"), position=position_fill(reverse=True)) + facet_grid("Rank ~ .")
    plt = plt + theme(axis_text_x = element_text(angle=90))
    plt.save(path/"plots/alt_ca_co_summary.pdf", height=210, width=297, units="mm")
    
    tmp = summary_alt_ca_co
    tmp["Pc_correct"] = tmp["Pc_correct"].astype(float)
    rank_cat = pd.api.types.CategoricalDtype(categories=["3","2","1"], ordered=True)
    tmp["Rank"] = tmp["Rank"].astype(str).astype(rank_cat)
    plt = ggplot(data=tmp) + geom_bar(aes(x="ID", y="Pc_correct", fill="Rank"), stat="identity")
    plt = plt + theme(axis_text_x=element_text(rotation=90, hjust=0.5))
    plt = plt + scale_y_continuous(breaks=np.linspace(0,1,11))
    plt.save(path/"plots/alt_ca_co_correct.pdf", height=210, width=297, units="mm")