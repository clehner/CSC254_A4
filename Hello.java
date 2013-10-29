public class Hello {
	public static void main(String[] args) {
		//print out something simply
		System.out.println("hello world!");

		//a simple loop
		int sum = 0;
		for(int i = 0; i < 100; i++) {
			sum += i;
		}
		System.out.println(sum);

		//now lets try instantiating a class!
		Class2 class2 = new Class2("dumb info");
		class2.print_info();
	}

	static int return1() {
		return 1;
	}
}

