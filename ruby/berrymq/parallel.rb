require 'thread'

module BerryMQ
  module ThreadPool
    @@qin = Queue.new
    @@qerr = Queue.new
    @@pool = []
    
    def self._report_error(error)
      @@qerr.push(error)
    end

    def self._get_all_from_queue(queue)
      while !queue.empty?
        begin
          yield queue.pop(non_block=ture)
        rescue ThreadError
          return
        end
      end
    end

    def self.do_work_form_queue
      while true
        command, target_method, message = @@qin.pop
        begin
          break if command == :stop
          if command == :process
            target_method.call(message)
          else
            raise ArgumentError.new("unknown command %s" % command)
          end
        rescue => exception
          self._report_error(exception)
        end
      end
    end

    def self.make_thread_pool(number)
      raise ArgumentError.new("'number' should be bigger than 0.") if number < 0
      number -= @@pool.size
      if number > 0
        number.times do
          new_thread = Thread.new do 
            BerryMQ::ThreadPool::do_work_form_queue
          end
          @@pool.push(new_thread)
        end
      elsif number < 0
        (number.abs).times do
          self.request_work(nil, nil, :stop)
        end
      end
    end

    def self.empty?
      while !@@qin.empty?
      end
      @@pool.empty?
    end

    def self.thread_count
      while !@@qin.empty?
      end
      self.clear_thread_pool
      @@pool.size
    end

    def self.clear_thread_pool
      alive_list = []
      @@pool.each do |thread|
        alive_list.push(thread) if thread.alive?
      end
      @@pool = alive_list
    end

    def self.request_work(target_function, message, command)
      @@qin.push([command, target_function, message])
    end

    def self.get_all_errors(&block)
      self._get_all_from_queue(@@qerr, &block)
    end

    def self.stop_thread_pool
      @@pool.each do
        self.request_work(nil, nil, :stop)
      end
      @@pool.each do |existing_thread|
        existing_thread.join
      end
      @@pool.clear
      @@qin.clear
    end
  end
end
