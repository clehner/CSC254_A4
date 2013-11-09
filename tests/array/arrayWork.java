//Lab 3 by Willie Reed (partner Jenny Uvina)

import java.util.*;

public class arrayWork
{
	public static void main(String[] args)
	{
		final int SIZE = 15;					//Part 1
		Random rand = new Random();
		
		int[] a = new int[SIZE];
		int[] b = new int[SIZE];
		int[] c = new int[SIZE];
		double [] d = new double[SIZE];
												//Part 2
		for(int i = 0; i<SIZE; i++)
		{
			d[i] = rand.nextDouble();
		}
		
		d[13] = 0.5;
		
		printArray(d);
		Arrays.sort(d);
		printArray(d);
		
		for(int i = 0; i<SIZE; i++)
		{
			a[i] = rand.nextInt(101);
		}
													//Part 3
		System.arraycopy(a, 0, b, 0, SIZE);
		printArray(a);
		printArray(b);
		
		Arrays.fill(c, 13);							//Part 4
		printArray(c);
													//Part 5
		System.out.println("Arrays one and two are equal: " + Arrays.equals(a, b));
		System.out.println("Arrays one and three are equal: " + Arrays.equals(a, c));
		
		
													//Part 6
		System.out.println("\nThe known value is at index: " + Arrays.binarySearch(d, 0.5));
		System.out.println("This is what happens when I search for something that's not here: " + 
			Arrays.binarySearch(d, 8.0));
		System.out.println("This is the binarySearch method with an unsorted array: " +
			Arrays.binarySearch(b, 3));
	
	
	}
													//Part 1 (cont.)
	public static void printArray(int[] arry)
	{
		for(int element : arry)
		{
			System.out.print(element + " \n");
		}
		System.out.println();
	}
	
	public static void printArray(double[] arry)
	{
		for(double element : arry)
		{
			System.out.print(element + " \n");
		}
		System.out.println();
	}
}
