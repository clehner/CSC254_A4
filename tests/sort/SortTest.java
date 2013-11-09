import java.util.Arrays;

public class SortTest
{ 
	static int count;
	
	public static void main(String[] args)
	{
		long startTime, endTime, elapsedTime;
		boolean print = true;
		int size = Integer.parseInt(args[0]);
		for(String str : args) if(str.equals("np")) print = false;
		
		Integer[] a = new Integer[size];
		Integer[] b = new Integer[size];
		
		for(int i=0; i<size; i++)
			a[i] = b[i] = (int)(Math.random() * 100);
			
		// maxSubSum4(testvect);
		
		// sum += (float)(endTime - startTime);
		
		if (print) printa(a);
		
		count = 0;
		
		startTime = System.currentTimeMillis();
		
		 //bubblesort(a);
		 //insertionsort(a);
		shellsort(a);
		// Arrays.sort(a);
		
		endTime = System.currentTimeMillis();
		
		elapsedTime = endTime - startTime;
		
		if (print) printa(a);
		
		// System.out.println("bubblesort took " + count + " moves to sort "
			// + size + " items");
		// System.out.println("\t in : "+ elapsedTime + " millisec");
		
		// System.out.println("insertsionsort took " + count + " moves to sort "
			// + size + " items");
		// System.out.println("\t in : "+ elapsedTime + " millisec");
		
		System.out.println("shellsort took " + count + " moves to sort "
			+ size + " items");
		System.out.println("\t in : "+ elapsedTime + " millisec");
		
		// System.out.println("Arrays.sort() took " + count + " moves to sort "
			// + size + " items");
		// System.out.println("\t in : "+ elapsedTime + " millisec");
		
		//restore array
		
		count = 0;
		
		for( int i=0; i<size; i++) a[i] = b[i];
		
	}
	
	
	public static <AnyType extends Comparable<? super AnyType>> void bubblesort(AnyType[] a)
	{
		for(int i=0; i<a.length; i++)
		{
			for(int j=0; j<a.length -1; j++)
			{
				if(a[j].compareTo(a[j+1]) > 0)
				{
					AnyType temp = a[j]; count++;
					a[j] = a[j+1]; count++;
					a[j+1] = temp; count++;
				}
			}
		}
	}
	
	public static <AnyType extends Comparable<? super AnyType>>	void insertionsort(AnyType[] a)
	{
		int j;
		
		for(int p=1; p<a.length; p++)
		{
			AnyType temp = a[p]; count++;
			for(j = p; j>0 && temp.compareTo(a[j-1]) < 0; j--)
				{a[j] = a[j-1]; count++;}
			a[j] = temp; count++;
		}
	}
	
	public static <AnyType extends Comparable<? super AnyType>>	void shellsort(AnyType[] a)
	{
		int j;
		int[] inc = getIncrements(a.length); 
		for(int e : inc) System.out.print(e + " "); System.out.println("\n");
		
		for(int i = inc.length - 1 ; i >= 0; i--)
		{
			for(int k = inc[i]; k < a.length; k++)
			{
				AnyType temp = a[k]; count++;
				for(j = k; j >= inc[i] && temp.compareTo(a[j - inc[i]]) < 0; j -= inc[i])
					{a[j] = a[j - inc[i]]; count++;}
				a[j] = temp; count++;
			}
		}
		
		
	}
	
	// public static int[] getIncrements(int size)
	// {
		// int[] inc;
		// int gap = 1;
		// for(int i=1; gap < size; i++)		
		// {
			// for(int k = 0; k < 1; k++) gap *= 2;
			// gap--;
			// inc[i] = gap;
			// gap = 1;
		// }
		
		// return inc;
	// }
	
	public static int[] getIncrements(int size)
	{
		int[] inc = new int[(int)(Math.log10(size)/Math.log10(2))]; 
		int i = 0; 
		for(int gap = 2; gap < size; gap *= 2)
		{
			inc[i] = gap - 1;
			i++;
		}
		
		return inc;
	}
		
	
	public static <AnyType extends Comparable<? super AnyType>>	void printa(AnyType[] a)
	{
		for(AnyType e : a)
			System.out.print(e.toString() + "  ");
		System.out.println("\n");
	}
}
	
