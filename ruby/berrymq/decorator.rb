require 'weakref'

module BerryMQ
  #
  #This module supports method decoration.
  #Internal use only
  #
  module DecoratorManager
    @@decorators = Hash.new do |hash, key| 
      hash[key] = {:is_init=>false, :decorators=>[]}
    end

    def self.new_decorator(klass, key, id_obj, args)
      @@decorators[klass][:decorators].push(Decorator.new(key, id_obj, args))
    end

    def self.method_added(klass, method_name)
      last_obj = @@decorators[klass][:decorators].last
      if last_obj != nil
        last_obj.method_name = method_name
        @@decorators[klass][:decorators].push(nil)
      end
    end

    def self.get(klass)
      @@decorators[klass][:decorators]
    end

    def self.is_init?(klass)
      @@decorators[klass][:is_init]
    end

    def self.set_init_flag(klass)
      @@decorators[klass][:is_init] = true
    end

    def self.decorate_object(target_obj)
      auto_twitter = nil
      if not self.is_init?(target_obj.class)
        self.get(target_obj.class).each do |decorator|
          next if decorator == nil
          if decorator.key == :auto_twitter
            self.override_method(target_obj, decorator)
          end
        end
        self.set_init_flag(target_obj.class)
      end
      self.get(target_obj.class).each do |decorator|
        next if decorator == nil
        if decorator.key == :following
          BerryMQ::RootTransporter::regist_follower(target_obj, decorator)
        end
      end
    end

    def self.override_method(target_obj, decorator)
      if decorator != nil
        id_obj = decorator.id
        target_method = decorator.method_name
        original_method = :"original_#{target_method}"
        entry_flag, exit_flag = decorator.args
        if entry_flag && exit_flag
          entry_id = BerryMQ::Identifier.new(id_obj, "entry")
          exit_id = BerryMQ::Identifier.new(id_obj, "exit")
          target_obj.class.class_eval do
            alias_method original_method, target_method
            define_method target_method do |*args|  
              BerryMQ::twitter(entry_id, args)
              result = __send__ original_method, *args  
              BerryMQ::twitter(exit_id, result)
              return result
            end  
          end
        elsif entry_flag == true
          entry_id = BerryMQ::Identifier.new(id_obj, "entry")
          target_obj.class.class_eval do
            alias_method original_method, target_method
            define_method target_method do |*args|
              BerryMQ::twitter(entry_id, args)
              __send__ original_method, *args  
            end  
          end
        elsif exit_flag == true
          exit_id = BerryMQ::Identifier.new(id_obj, "exit")
          target_obj.class.class_eval do
            alias_method original_method, target_method
            define_method target_method do |*args|  
              result = __send__ original_method, *args
              BerryMQ::twitter(exit_id, result)
              return result
            end  
          end
        end
      end
    end
  end
  class Decorator
    attr_reader :key, :args, :method_name, :id
    attr_writer :method_name
    def initialize(key, id_obj, args)
      @key = key
      @id = id_obj
      @args = args
      @method_name = nil
    end
  end
  class WeakRefMethod
    attr_reader :method_name
    def initialize(target_obj, method_name)
      @target_obj = WeakRef.new(target_obj)
      @method_name = method_name
    end
    def call(args)
      @target_obj.__send__(@method_name, *args)
    end
    def alive?
      @target_obj.weakref_alive?
    end
  end
end
