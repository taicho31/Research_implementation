#define _CRT_SECURE_NO_WARNINGS
#define RA 5036765
#define CA 37
#define RB 129843
#define CB 32
#define RC 13268
#define CC 37
#define RE 3456
#define CE 41
#define RD 54603
#define CD 33
#define I  12 /* inning*/
#define T  2 /* team*/
#define W  4
#define S 70
#define R1 10 /* 1st base runner's order*/
#define R2 2 /* 2nd base runner ot not*/
#define R3 2 /* 3rd base runner ot not*/
#define B1 9
#define B2 9
#define UNCHECK -1
#define NAME 9
#define RESULT 9

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <fstream>
#include <vector>
#include <iostream>
#include <sstream>
using namespace std;

double omote[NAME][RESULT], ura[NAME][RESULT];
int carpdoubleplay12, giantsdoubleplay12 = 0;
int carpdoubleplay13, giantsdoubleplay13 = 0;
int hamudoubleplay12, hamudoubleplay13 = 0;
int sbankdoubleplay12, sbankdoubleplay13 = 0;
int ckikai12, ckikai13, gkikai12, gkikai13 = 0;
int nkikai12, nkikai13, skikai12, skikai13 = 0;
double cdourate12, cdourate13, gdourate12, gdourate13, sdourate12, sdourate13, hdourate12, hdourate13;
double table[I][T][W][S][R1][R2][R3][B1][B2];
double btable[I][T][W][S][R1][R2][R3][B1][B2];
char stable[I][T][W][S][R1][R2][R3][B1][B2];
int i, t, w, s, r1, r2, r3, b1, b2;

/*Kira,Inakawaの再現*/
//r1について…0から8番が打順、9は一塁にランナーがいないときとする//
//2,3塁での併殺打はないものとするかもしれない//
//打撃、盗塁、犠打の中で勝率の最大値を計算するための関数//

double maxof(double a, double b, double c)
{
	double saidai = a;

	if (saidai < b)
		saidai = b;
	if (saidai < c)
		saidai = c;
	return saidai;
}

double maxtw(double a, double b)
{
	double saidai = a;

	if (saidai < b)
		saidai = b;

	return saidai;
}

double minof(double a, double b, double c)
{
	double sisyo = a;

	if (sisyo > b)
		sisyo = b;
	if (sisyo > c)
		sisyo = c;
	return sisyo;
}

double mintw(double a, double b)
{
	double sisyo = a;

	if (sisyo > b)
		sisyo = b;

	return sisyo;
}

double calc(int i, int t, int w, int s, int r1, int r2, int r3, int b1, int b2)
{

	b1 = b1 % 9;  /*0,1,2,3,4,5,6,7,8,0,1…*/
	b2 = b2 % 9;  /*0,1,2,3,4,5,6,7,8,0,1…*/
	t = t % 2;    /*0,1,0,1*/
	if (w > 3) w = 3;
	double a, b, c, d,e,f;  /*a:打撃併殺あり,b:盗塁,c:犠打,d:打撃併殺なし,e:敬遠,f:打撃併殺あり無得点したときの勝率*/


	/*printf("先攻チーム%d,%d,%d,%d,%d,%d,%d,%d,%d: %f \n", i, t, w, s, r1, r2, r3, b1, b2, table[i][t][w][s][r1][r2][r3][b1][b2]);*/


	if (table[i][t][w][s][r1][r2][r3][b1][b2] != UNCHECK)
		return table[i][t][w][s][r1][r2][r3][b1][b2];

	else if (i >= 8 && t == 1 && w == 3 && s > 35)
	{
		stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
		return  table[i][t][w][s][r1][r2][r3][b1][b2] = 1;
	}
	else if ((i == 8 && t == 0 && w == 3 && s < 35) || (i >= 8 && t == 1 && s < 35))
	{
		stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
		return  table[i][t][w][s][r1][r2][r3][b1][b2] = 0;
	}
	else if (i == 11 && t == 1 && w == 3 && s == 35)
	{
		stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
		return  table[i][t][w][s][r1][r2][r3][b1][b2] = 0;
	}
	else if (s >= 65)
	{
		stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
		return  table[i][t][w][s][r1][r2][r3][b1][b2] = 1;
	}
	else if (s <= 5)
	{
		stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
		return  table[i][t][w][s][r1][r2][r3][b1][b2] = 0;
	}                                                                   /*ここまで吸収状態*/

	/* ランナーなし   盗塁、犠打なし  凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 == 9 && r2 == 0 && r3 == 0)
	{

		if (t == 0){
			if (w < 3)
			{
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
				return table[i][t][w][s][r1][r2][r3][b1][b2] =
					omote[b1][0] * calc(i, t, w + 1, s, 9, 0, 0, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s, b1, 0, 0, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 1, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 0, 0, b1 + 1, b2);
			}
			else
			{
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
		}
		else
		{
			if (w < 3)
			{
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
				return table[i][t][w][s][r1][r2][r3][b1][b2] =
					ura[b2][0] * calc(i, t, w + 1, s, 9, 0, 0, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s, b2, 0, 0, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 1, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 0, 0, b1, b2 + 1);
			}
			else
			{
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
		}
	}

	/* ランナー一塁   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 != 9 && r2 == 0 && r3 == 0)
	{
		if (t == 0){
			if (w == 3)
			{
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
			else
			{
				a = (omote[b1][0] - omote[b1][8]) * calc(i, t, w + 1, s, r1, 0, 0, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 1, 0, b1 + 1, b2)
					+ omote[b1][8] * calc(i, t, w + 2, s, 9, 0, 0, b1 + 1, b2);

				b = omote[b1][6] * calc(i, t, w, s, 9, 1, 0, b1, b2) + (1.0 - omote[b1][6])*calc(i, t, w + 1, s, 9, 0, 0, b1, b2);

				c = omote[b1][7] * calc(i, t, w + 1, s, 9, 1, 0, b1 + 1, b2) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2);

				d =  omote[b1][0]  * calc(i, t, w + 1, s, r1, 0, 0, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 1, 0, b1 + 1, b2);

				if (w == 0 || w == 1)
				{

					if (a == maxof(a, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					else if (b == maxof(a, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxof(a, b, c);
				}
				else
				{

					if (b == maxtw(b, d)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(d, b);
				}
			}
		}
		else{
			if (w == 3)
			{
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return  table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
			else
			{
				a = (ura[b2][0] - ura[b2][8]) * calc(i, t, w + 1, s, r1, 0, 0, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 1, 0, b1, b2 + 1)
					+ ura[b2][8] * calc(i, t, w + 2, s, 9, 0, 0, b1, b2 + 1);

				b = ura[b2][6] * calc(i, t, w, s, 9, 1, 0, b1, b2) + (1.0 - ura[b2][6]) * calc(i, t, w + 1, s, 9, 0, 0, b1, b2);

				c = ura[b2][7] * calc(i, t, w + 1, s, 9, 1, 0, b1, b2 + 1) + (1.0 - ura[b2][7]) *calc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1);

				d = ura[b2][0] * calc(i, t, w + 1, s, r1, 0, 0, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 1, 0, b1, b2 + 1);

				if (w == 0 || w == 1)
				{

					if (a == minof(a, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					else if (b == minof(a, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = minof(a, b, c);
				}
				else
				{

					if (b == mintw(d, b)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = mintw(d, b);
				}
			}
		}
	}

	/* ランナー2塁    盗塁なし    凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 == 9 && r2 == 1 && r3 == 0)
	{
		if (t == 0){
			if (w == 3){
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
			else
			{
				a = omote[b1][0] * calc(i, t, w + 1, s, 9, 1, 0, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 0, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 1, 0, b1 + 1, b2);
				c = omote[b1][7] * calc(i, t, w + 1, s, 9, 0, 1, b1 + 1, b2) + (1.0 - omote[b1][7]) * calc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2);


				if (w == 0 || w == 1)
				{

					if (c == maxtw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}
				else
				{

					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
		else
		{
			if (w == 3) {
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
			else
			{
				a = ura[b2][0] * calc(i, t, w + 1, s, 9, 1, 0, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 0, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 1, 0, b1, b2 + 1);
				c = ura[b2][7] * calc(i, t, w + 1, s, 9, 0, 1, b1, b2 + 1) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1);

				if (w == 0 || w == 1)
				{

					if (c == mintw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}
				else
				{

					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
	}

	/*ランナー3塁   盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 == 9 && r2 == 0 && r3 == 1)
	{
		if (t == 0){
			if (w == 3) {
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return  table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			}

			else
			{
				a = omote[b1][0] * calc(i, t, w + 1, s, 9, 0, 1, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 0, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 0, 1, b1 + 1, b2);
				c = omote[b1][7] * calc(i, t, w + 1, s + 1, 9, 0, 0, b1 + 1, b2) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2);

				if (w == 0 || w == 1)
				{

					if (c == maxtw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}

				else
				{

					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
		else
		{
			if (w == 3) {
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
			else
			{
				a = ura[b2][0] * calc(i, t, w + 1, s, 9, 0, 1, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 0, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 0, 1, b1, b2 + 1);
				c = ura[b2][7] * calc(i, t, w + 1, s - 1, 9, 0, 0, b1, b2 + 1) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1);

				if (w == 0 || w == 1)
				{

					if (c == mintw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}
				else
				{

					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}

			}
		}
	}

	/* ランナー1,2塁    　盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 != 9 && r2 == 1 && r3 == 0)
	{
		if (t == 0){
			if (w == 3) {
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return  table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
			else
			{
				a = (omote[b1][0]-omote[b1][8]) * calc(i, t, w + 1, s, r1, 1, 0, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2)
					+ omote[b1][8] * calc(i, t, w + 2, s, 9, 0, 1, b1 + 1, b2);
				c = omote[b1][7] * calc(i, t, w + 1, s, 9, 1, 1, b1 + 1, b2) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 1, 0, b1 + 1, b2);
				d = omote[b1][0] * calc(i, t, w + 1, s, r1, 1, 0, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2);
				if (w == 0 || w == 1)
				{

					if (c == maxtw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}
				else
				{

					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = d;
				}
			}
		}
		else
		{
			if (w == 3) {
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return  table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
			else
			{
				a = (ura[b2][0]-ura[b2][8]) * calc(i, t, w + 1, s, r1, 1, 0, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1)
					+ ura[b2][8] * calc(i, t, w + 2, s, 9, 0, 1, b1, b2 + 1);
				c = ura[b2][7] * calc(i, t, w + 1, s, 9, 1, 1, b1, b2 + 1) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 1, 0, b1, b2 + 1);
				d = ura[b2][0] * calc(i, t, w + 1, s, r1, 1, 0, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1);

				if (w == 0 || w == 1)
				{

					if (c == mintw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}

				else
				{

					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = d;
				}

			}
		}
	}

	/* ランナー2,3塁    盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順   */
	else if (r1 == 9 && r2 == 1 && r3 == 1)
	{
		if (t == 0){
			if (w == 3) {
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return  table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			}

			else
			{
				a = omote[b1][0] * calc(i, t, w + 1, s, 9, 1, 1, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 2, b1, 0, 0, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2);
				c = omote[b1][7] * calc(i, t, w + 1, s + 1, 9, 0, 1, b1 + 1, b2) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 0, 1, b1 + 1, b2);

				if (w == 0 || w == 1)
				{

					if (c == maxtw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}
				else
				{
					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
		else
		{
			if (w == 3){
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return  table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			}

			else
			{
				a = ura[b2][0] * calc(i, t, w + 1, s, 9, 1, 1, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 2, b2, 0, 0, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1);
				c = ura[b2][7] * calc(i, t, w + 1, s - 1, 9, 0, 1, b1, b2 + 1) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 0, 1, b1, b2 + 1);

				if (w == 0 || w == 1)
				{

					if (c == mintw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}

				else
				{

					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
	}

	/*ランナー1,3塁  凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 != 9 && r2 == 0 && r3 == 1)
	{
		if (t == 0){
			if (w == 3)  {
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			}

			else
			{
				a = (omote[b1][0]-omote[b1][8]) * calc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2)
					+ omote[b1][8] * calc(i, t, w + 2, s+1, 9, 0, 0, b1 + 1, b2);
				b = omote[b1][6] * calc(i, t, w, s, 9, 1, 1, b1, b2) + (1 - omote[b1][6]) * calc(i, t, w + 1, s, 9, 0, 1, b1, b2);
				c = omote[b1][7] * calc(i, t, w + 1, s + 1, 9, 1, 0, b1 + 1, b2) + (1.0 - omote[b1][7]) * calc(i, t, w + 1, s, b1, 1, 0, b1 + 1, b2);
				d = omote[b1][0] * calc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2);
				f = (omote[b1][0] - omote[b1][8]) * calc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2)
					+ omote[b1][8] * calc(i, t, w + 2, s, 9, 0, 0, b1 + 1, b2);
				if (w == 0 )
				{

					if (a == maxof(a, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					else if (b == maxof(a, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxof(a, b, c);
				}
				else if (w == 1)
				{
					if (f == maxof(f, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					else if (b == maxof(f, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxof(f, b, c);
				}
				else
				{

					if (b == maxtw(b, d)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(b, d);
				}
			}
		}
		else
		{
			if (w == 3) {
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			}

			else
			{
				a = (ura[b2][0]-ura[b2][8]) * calc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1)
					+ ura[b2][8] * calc(i, t, w + 2, s-1, 9, 0, 0, b1, b2 + 1);
				b = ura[b2][6] * calc(i, t, w, s, 9, 1, 1, b1, b2) + (1 - ura[b2][6])*calc(i, t, w + 1, s, 9, 0, 1, b1, b2);
				c = ura[b2][7] * calc(i, t, w + 1, s - 1, 9, 1, 0, b1, b2 + 1) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 1, 0, b1, b2 + 1);
				d = ura[b2][0] * calc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1);
				f = (ura[b2][0]-ura[b2][8]) * calc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1)
					+ ura[b2][8] * calc(i, t, w + 2, s, 9, 0, 0, b1, b2 + 1);
				if (w == 0)
				{
					if (a == minof(a, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					else if (b == minof(a, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = minof(a, b, c);
				}
				else if (w == 1)
				{
					if (f == minof(f, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					else if (b == minof(f, b, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = minof(f, b, c);
				}
				else
				{

					if (b == mintw(b, d)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = mintw(b, d);
				}
			}
		}
	}

	/*ランナー満塁   盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 != 9 && r2 == 1 && r3 == 1)
	{
		if (t == 0){
			if (w == 3)
			{
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return  table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
			else
			{
				a = (omote[b1][0]-omote[b1][8]) * calc(i, t, w + 1, s, r1, 1, 1, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 2, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 3, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 3, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 4, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s + 1, b1, 1, 1, b1 + 1, b2)
					+ omote[b1][8] * calc(i, t, w + 2, s, 9, 1, 1, b1 + 1, b2);
				c = omote[b1][7] * calc(i, t, w + 1, s + 1, 9, 1, 1, b1 + 1, b2) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 1, 1, b1 + 1, b2);
				d = omote[b1][0] * calc(i, t, w + 1, s, r1, 1, 1, b1 + 1, b2) + omote[b1][1] * calc(i, t, w, s + 2, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * calc(i, t, w, s + 3, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * calc(i, t, w, s + 3, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * calc(i, t, w, s + 4, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * calc(i, t, w, s + 1, b1, 1, 1, b1 + 1, b2);
		
				if (w == 0 || w == 1)
				{

					if (c == maxtw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}
				else
				{

					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = d;

				}
			}
		}
		else
		{
			if (w == 3) {
				stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
				return table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			}
			else
			{
				a = (ura[b2][0]-ura[b2][8]) * calc(i, t, w + 1, s, r1, 1, 1, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 2, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 3, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 3, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 4, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s - 1, b2, 1, 1, b1, b2 + 1)
					+ ura[b2][8] * calc(i, t, w + 2, s, 9, 1, 1, b1, b2 + 1);
				c = ura[b2][7] * calc(i, t, w + 1, s - 1, 9, 1, 1, b1, b2 + 1) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 1, 1, b1, b2 + 1);
				d = ura[b2][0] * calc(i, t, w + 1, s, r1, 1, 1, b1, b2 + 1) + ura[b2][1] * calc(i, t, w, s - 2, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * calc(i, t, w, s - 3, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * calc(i, t, w, s - 3, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * calc(i, t, w, s - 4, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * calc(i, t, w, s - 1, b2, 1, 1, b1, b2 + 1);
				if (w == 0 || w == 1)
				{

					if (c == mintw(a, c)) stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B';
					else stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}
				else
				{

					stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H';
					return table[i][t][w][s][r1][r2][r3][b1][b2] = d;
				}

			}
		}
	}
	else {
		stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N';
		return table[i][t][w][s][r1][r2][r3][b1][b2] = 0;
	}
}


/*後攻チームの勝率を計算*/
double bcalc(int i, int t, int w, int s, int r1, int r2, int r3, int b1, int b2)
{

	b1 = b1 % 9;  /*0,1,2,3,4,5,6,7,8,0,1…*/
	b2 = b2 % 9;  /*0,1,2,3,4,5,6,7,8,0,1…*/
	t = t % 2;    /*0,1,0,1*/
	if (w > 3) w = 3;
	double a, b, c,d, e,f;  /*a:打撃,b:盗塁,c:犠打,e:敬遠したときの勝率*/


	/*printf("%d,%d,%d,%d,%d,%d,%d,%d,%d: %f\n", i, t, w, s, r1, r2, r3, b1, b2, table[i][t][w][s][r1][r2][r3][b1][b2]);*/


	if (btable[i][t][w][s][r1][r2][r3][b1][b2] != UNCHECK)
		return btable[i][t][w][s][r1][r2][r3][b1][b2];

	else if (i >= 8 && t == 1 && w == 3 && s > 35)
		return  btable[i][t][w][s][r1][r2][r3][b1][b2] = 0;

	else if ((i == 8 && t == 0 && w == 3 && s < 35) || (i >= 8 && t == 1 && s < 35))
		return  btable[i][t][w][s][r1][r2][r3][b1][b2] = 1;

	else if (i == 11 && t == 1 && w == 3 && s == 35)
		return  btable[i][t][w][s][r1][r2][r3][b1][b2] = 0;

	else if (s >= 65)
		return  btable[i][t][w][s][r1][r2][r3][b1][b2] = 0;

	else if (s <= 5)
		return  btable[i][t][w][s][r1][r2][r3][b1][b2] = 1;     /*ここまで吸収状態*/

	/* ランナーなし   盗塁、犠打なし  凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 == 9 && r2 == 0 && r3 == 0)
	{
		if (t == 0){
			if (w < 3)
				return btable[i][t][w][s][r1][r2][r3][b1][b2] =
				omote[b1][0] * bcalc(i, t, w + 1, s, 9, 0, 0, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s, b1, 0, 0, b1 + 1, b2)
				+ omote[b1][2] * bcalc(i, t, w, s, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s, 9, 0, 1, b1 + 1, b2)
				+ omote[b1][4] * bcalc(i, t, w, s + 1, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 0, 0, b1 + 1, b2);
			else
				return btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
		}
		else
		{
			if (w < 3)
				return btable[i][t][w][s][r1][r2][r3][b1][b2] =
				ura[b2][0] * bcalc(i, t, w + 1, s, 9, 0, 0, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s, b2, 0, 0, b1, b2 + 1)
				+ ura[b2][2] * bcalc(i, t, w, s, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s, 9, 0, 1, b1, b2 + 1)
				+ ura[b2][4] * bcalc(i, t, w, s - 1, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 0, 0, b1, b2 + 1);
			else
				return btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
		}
	}

	/* ランナー一塁   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 != 9 && r2 == 0 && r3 == 0)
	{
		if (t == 0){
			if (w == 3)
				return btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = (omote[b1][0]-omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 0, 0, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 0, b1 + 1, b2)
					+ omote[b1][8] * bcalc(i, t, w + 2, s, 9, 0, 0, b1 + 1, b2);

				b = omote[b1][6] * bcalc(i, t, w, s, 9, 1, 0, b1, b2) + (1.0 - omote[b1][6]) * bcalc(i, t, w + 1, s, 9, 0, 0, b1, b2);

				c = omote[b1][7] * bcalc(i, t, w + 1, s, 9, 1, 0, b1 + 1, b2) + (1.0 - omote[b1][7])*bcalc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2);

				d = omote[b1][0] * bcalc(i, t, w + 1, s, r1, 0, 0, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 0, b1 + 1, b2);

				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = minof(a, b, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = mintw(b, d);
				}
			}
		}
		else{
			if (w == 3)
				return  btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 0, 0, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 0, b1, b2 + 1)
					+ ura[b2][8] * bcalc(i, t, w + 2, s, 9, 0, 0, b1, b2 + 1);

				b = ura[b2][6] * bcalc(i, t, w, s, 9, 1, 0, b1, b2) + (1.0 - ura[b2][6]) * bcalc(i, t, w + 1, s, 9, 0, 0, b1, b2);

				c = ura[b2][7] * bcalc(i, t, w + 1, s, 9, 1, 0, b1, b2 + 1) + (1.0 - ura[b2][7]) * bcalc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1);

				d = ura[b2][0] * bcalc(i, t, w + 1, s, r1, 0, 0, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 0, b1, b2 + 1);

				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxof(a, b, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(b, d);
				}
			}
		}
	}

	/* ランナー2塁    盗塁なし    凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 == 9 && r2 == 1 && r3 == 0)
	{
		if (t == 0){
			if (w == 3)return btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = omote[b1][0] * bcalc(i, t, w + 1, s, 9, 1, 0, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 0, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 0, b1 + 1, b2);
				c = omote[b1][7] * bcalc(i, t, w + 1, s, 9, 0, 1, b1 + 1, b2) + (1.0 - omote[b1][7]) * bcalc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2);

				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
		else
		{
			if (w == 3)  return btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = ura[b2][0] * bcalc(i, t, w + 1, s, 9, 1, 0, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 0, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 0, b1, b2 + 1);
				c = ura[b2][7] * bcalc(i, t, w + 1, s, 9, 0, 1, b1, b2 + 1) + (1.0 - ura[b2][7])*bcalc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1);

				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
	}

	/*ランナー3塁   盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 == 9 && r2 == 0 && r3 == 1)
	{
		if (t == 0){
			if (w == 3)  return  btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = omote[b1][0] * bcalc(i, t, w + 1, s, 9, 0, 1, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 0, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 0, 1, b1 + 1, b2);
				c = omote[b1][7] * bcalc(i, t, w + 1, s + 1, 9, 0, 0, b1 + 1, b2) + (1.0 - omote[b1][7])*bcalc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2);

				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
		else
		{
			if (w == 3)  return btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = ura[b2][0] * bcalc(i, t, w + 1, s, 9, 0, 1, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 0, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 0, 1, b1, b2 + 1);
				c = ura[b2][7] * bcalc(i, t, w + 1, s - 1, 9, 0, 0, b1, b2 + 1) + (1.0 - ura[b2][7])*bcalc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1);

				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
	}

	/* ランナー1,2塁    　盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 != 9 && r2 == 1 && r3 == 0)
	{
		if (t == 0){
			if (w == 3)  return  btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = (omote[b1][0]-omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 1, 0, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2)
					+ omote[b1][8] * bcalc(i, t, w + 2, s, 9, 0, 1, b1 + 1, b2);
				c = omote[b1][7] * bcalc(i, t, w + 1, s, 9, 1, 1, b1 + 1, b2) + (1.0 - omote[b1][7]) * bcalc(i, t, w + 1, s, b1, 1, 0, b1 + 1, b2);
				d = omote[b1][0] * bcalc(i, t, w + 1, s, r1, 1, 0, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2);
				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = d;
				}
			}
		}
		else
		{
			if (w == 3)  return  btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 1, 0, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1)
					+ ura[b2][8] * bcalc(i, t, w + 2, s, 9, 0, 1, b1, b2 + 1);
				c = ura[b2][7] * bcalc(i, t, w + 1, s, 9, 1, 1, b1, b2 + 1) + (1.0 - ura[b2][7]) * bcalc(i, t, w + 1, s, b2, 1, 0, b1, b2 + 1);
				d = ura[b2][0] * bcalc(i, t, w + 1, s, r1, 1, 0, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1);
				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = d;
				}
			}
		}
	}

	/* ランナー2,3塁    盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順   併殺打はどうするか？*/
	else if (r1 == 9 && r2 == 1 && r3 == 1)
	{
		if (t == 0){
			if (w == 3)  return  btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = omote[b1][0] * bcalc(i, t, w + 1, s, 9, 1, 1, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 2, b1, 0, 0, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2);
				c = omote[b1][7] * bcalc(i, t, w + 1, s + 1, 9, 0, 1, b1 + 1, b2) + (1.0 - omote[b1][7]) * bcalc(i, t, w + 1, s, b1, 0, 1, b1 + 1, b2);

				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
		else
		{
			if (w == 3) return  btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = ura[b2][0] * bcalc(i, t, w + 1, s, 9, 1, 1, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 2, b2, 0, 0, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1);
				c = ura[b2][7] * bcalc(i, t, w + 1, s - 1, 9, 0, 1, b1, b2 + 1) + (1.0 - ura[b2][7])* bcalc(i, t, w + 1, s, b2, 0, 1, b1, b2 + 1);

				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = a;
				}
			}
		}
	}

	/*ランナー1,3塁  凡退、併殺打、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 != 9 && r2 == 0 && r3 == 1)
	{
		if (t == 0){
			if (w == 3)    return btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = (omote[b1][0]-omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2)
					+ omote[b1][8] * bcalc(i, t, w + 2, s+1, 9, 0, 0, b1 + 1, b2);
				b = omote[b1][6] * bcalc(i, t, w, s, 9, 1, 1, b1, b2) + (1 - omote[b1][6]) * bcalc(i, t, w + 1, s, 9, 0, 1, b1, b2);
				c = omote[b1][7] * bcalc(i, t, w + 1, s + 1, 9, 1, 0, b1 + 1, b2) + (1.0 - omote[b1][7]) * bcalc(i, t, w + 1, s, b1, 1, 0, b1 + 1, b2);
				d = omote[b1][0] * bcalc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2);
				f = (omote[b1][0] - omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2)
					+ omote[b1][8] * bcalc(i, t, w + 2, s , 9, 0, 0, b1 + 1, b2);

				if (w == 0 )
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = minof(a, b, c);
				}
				else if (w == 1)
				{
					return btable[i][t][w][s][r1][r2][r3][b1][b2] = minof(f, b, c);
				}
				else
				{
					return btable[i][t][w][s][r1][r2][r3][b1][b2] = mintw(b, d);
				}
			}
		}
		else
		{
			if (w == 3)   return btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1)
					+ ura[b2][8] * bcalc(i, t, w + 2, s-1, 9, 0, 0, b1, b2 + 1);
				b = ura[b2][6] * bcalc(i, t, w, s, 9, 1, 1, b1, b2) + (1 - ura[b2][6])*bcalc(i, t, w + 1, s, 9, 0, 1, b1, b2);
				c = ura[b2][7] * bcalc(i, t, w + 1, s - 1, 9, 1, 0, b1, b2 + 1) + (1.0 - ura[b2][7])*bcalc(i, t, w + 1, s, b2, 1, 0, b1, b2 + 1);
				d = ura[b2][0] * bcalc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1);
				f = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1)
					+ ura[b2][8] * bcalc(i, t, w + 2, s, 9, 0, 0, b1, b2 + 1);

				if (w == 0)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxof(a, b, c);
				}
				else if (w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxof(f, b, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(b, d);
				}
			}
		}
	}

	/*ランナー満塁   盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
	else if (r1 != 9 && r2 == 1 && r3 == 1)
	{
		if (t == 0){
			if (w == 3) return  btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = (omote[b1][0]-omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 1, 1, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 2, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 3, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 3, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 4, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s + 1, b1, 1, 1, b1 + 1, b2)
					+ omote[b1][8] * bcalc(i, t, w + 2, s, 9, 1, 1, b1 + 1, b2);
				c = omote[b1][7] * bcalc(i, t, w + 1, s + 1, 9, 1, 1, b1 + 1, b2) + (1.0 - omote[b1][7])*bcalc(i, t, w + 1, s, b1, 1, 1, b1 + 1, b2);
				d = omote[b1][0] * bcalc(i, t, w + 1, s, r1, 1, 1, b1 + 1, b2) + omote[b1][1] * bcalc(i, t, w, s + 2, b1, 0, 1, b1 + 1, b2)
					+ omote[b1][2] * bcalc(i, t, w, s + 3, 9, 1, 0, b1 + 1, b2) + omote[b1][3] * bcalc(i, t, w, s + 3, 9, 0, 1, b1 + 1, b2)
					+ omote[b1][4] * bcalc(i, t, w, s + 4, 9, 0, 0, b1 + 1, b2) + omote[b1][5] * bcalc(i, t, w, s + 1, b1, 1, 1, b1 + 1, b2);

				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = mintw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = d;
				}
			}
		}
		else
		{
			if (w == 3)  	return btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2);
			else
			{
				a = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 1, 1, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 2, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 3, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 3, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 4, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s - 1, b2, 1, 1, b1, b2 + 1)
					+ ura[b2][8] * bcalc(i, t, w + 2, s, 9, 1, 1, b1, b2 + 1);
				c = ura[b2][7] * bcalc(i, t, w + 1, s - 1, 9, 1, 1, b1, b2 + 1) + (1.0 - ura[b2][7]) * bcalc(i, t, w + 1, s, b2, 1, 1, b1, b2 + 1);
				d = ura[b2][0] * bcalc(i, t, w + 1, s, r1, 1, 1, b1, b2 + 1) + ura[b2][1] * bcalc(i, t, w, s - 2, b2, 0, 1, b1, b2 + 1)
					+ ura[b2][2] * bcalc(i, t, w, s - 3, 9, 1, 0, b1, b2 + 1) + ura[b2][3] * bcalc(i, t, w, s - 3, 9, 0, 1, b1, b2 + 1)
					+ ura[b2][4] * bcalc(i, t, w, s - 4, 9, 0, 0, b1, b2 + 1) + ura[b2][5] * bcalc(i, t, w, s - 1, b2, 1, 1, b1, b2 + 1);
				if (w == 0 || w == 1)
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = maxtw(a, c);
				}
				else
				{

					return btable[i][t][w][s][r1][r2][r3][b1][b2] = d;
				}
			}
		}
	}
	else return btable[i][t][w][s][r1][r2][r3][b1][b2] = 0;

}

int main(void)
{
	time_t start, end;
	double diff;
	start = clock();

	double tmp;

	/*先攻チームのデータ読み取り*/
	FILE *ff = fopen("data/giants.txt", "r");

	for (int i = 0; i < NAME; i++){
		for (int j = 0; j < RESULT; j++)
		{
			fscanf(ff, "%lf", &omote[i][j]);
		}
	}    

	/*後攻チームのcsvデータ読み取り*/
	FILE *fg = fopen("data/carp.txt", "r");

	for (int i = 0; i < NAME; i++){
		for (int j = 0; j < RESULT; j++)
		{
			fscanf(fg, "%lf", &ura[i][j]);
		}
	}	

	for (i = 0; i < I; i++){
		for (t = 0; t < T; t++){
			for (w = 0; w < W; w++){
				for (s = 0; s < S; s++){
					for (r1 = 0; r1 < R1; r1++){
						for (r2 = 0; r2 < R2; r2++){
							for (r3 = 0; r3 < R3; r3++){
								for (b1 = 0; b1 < B1; b1++){
									for (b2 = 0; b2 < B2; b2++){
										table[i][t][w][s][r1][r2][r3][b1][b2] = UNCHECK;
										btable[i][t][w][s][r1][r2][r3][b1][b2] = UNCHECK;
									}
								}
							}
						}
					}
				}
			}
		}
	}

	printf("試合開始の先攻の勝率:%f\n", calc(0, 0, 0, 35, 9, 0, 0, 0, 0));
	printf("試合開始の後攻の勝率:%f\n", bcalc(0, 0, 0, 35, 9, 0, 0, 0, 0));

	end = clock();
	diff = (double)(end - start) / CLOCKS_PER_SEC;

	printf("time %.3f sec\n", diff);

	return 0;
}
